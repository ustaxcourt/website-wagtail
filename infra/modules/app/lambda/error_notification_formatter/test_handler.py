"""Unit tests for the error notification formatter Lambda handler."""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("SENDER_EMAIL", "noreply@example.com")
os.environ.setdefault("RECIPIENT_EMAILS", "dev@example.com,manager@example.com")
os.environ.setdefault("APP_LOG_GROUP_NAME", "/ecs/production-website-logs")
os.environ.setdefault(
    "RDS_LOG_GROUP_NAME", "/aws/rds/instance/production-db/postgresql"
)

import handler  # noqa: E402


def _sns_event(alarm_message: dict) -> dict:
    return {"Records": [{"Sns": {"Message": json.dumps(alarm_message)}}]}


class BuildEmailTests(unittest.TestCase):
    def test_5xx_alarm_produces_readable_subject_and_body(self):
        alarm_message = {
            "AlarmName": "production-5xx-error-alarm",
            "AlarmDescription": "This metric monitors for 5xx errors in the website logs",
            "StateChangeTime": "2026-08-06T14:32:00.000+0000",
            "NewStateReason": "Threshold Crossed: 1 datapoint [2.0 (06/08/26 13:32:00)] was greater than the threshold (1.0).",
            "Trigger": {"Period": 3600, "EvaluationPeriods": 1},
        }

        subject, text_body, html_body = handler.build_email(alarm_message, "us-east-1")

        self.assertEqual(
            subject, "Production website error detected: Server errors (5xx)"
        )
        self.assertIn("Error Summary", text_body)
        self.assertIn("What happened: Threshold Crossed", text_body)
        self.assertIn("Environment: production", text_body)
        self.assertIn(
            "Open matching log events: https://us-east-1.console.aws.amazon.com",
            text_body,
        )
        self.assertIn("/log-events", text_body)
        self.assertIn(
            "Suggested filter pattern: { $.status_code >= 500 && $.status_code < 600 }",
            text_body,
        )
        self.assertIn("Suggested time window:", text_body)
        self.assertIn("Technical details (for developers)", text_body)
        self.assertIn("<h2>Error Summary</h2>", html_body)
        self.assertIn("<strong>What happened:</strong>", html_body)
        self.assertIn(
            "<strong><u>Technical details (for developers)</u></strong>", html_body
        )
        # Raw JSON must still be present, but only after the human-readable summary.
        self.assertLess(
            text_body.index("What happened"), text_body.index("Technical details")
        )

    def test_404_alarm_uses_state_reason_and_filter_guidance(self):
        alarm_message = {
            "AlarmName": "sandbox-404-error-alarm",
            "AlarmDescription": "This metric monitors for 404 errors in the website logs",
            "StateReason": "Threshold Crossed: 1 datapoint [102.0 (12/08/26 18:58:00)] was greater than the threshold (50.0).",
            "StateChangeTime": "2026-08-12T19:58:21.151+0000",
            "Trigger": {"Period": 3600, "EvaluationPeriods": 1},
        }

        _, text_body, html_body = handler.build_email(alarm_message, "us-east-1")

        self.assertIn("What happened: Threshold Crossed: 1 datapoint [102.0", text_body)
        self.assertIn("Suggested filter pattern: { $.status_code = 404 }", text_body)
        self.assertIn("Log group: /ecs/production-website-logs", text_body)
        self.assertIn("<strong>Environment:</strong> sandbox", html_body)

    def test_unrecognized_alarm_falls_back_to_generic_label(self):
        alarm_message = {"AlarmName": "train-some-other-alarm", "StateChangeTime": ""}

        subject, _, _ = handler.build_email(alarm_message, "us-east-1")

        self.assertEqual(subject, "Train website error detected: An error")


class LambdaHandlerTests(unittest.TestCase):
    @patch("handler.ses_client")
    def test_sends_one_email_per_record_to_all_recipients(self, mock_ses):
        event = _sns_event(
            {"AlarmName": "sandbox-404-error-alarm", "StateChangeTime": ""}
        )

        handler.lambda_handler(event, MagicMock())

        mock_ses.send_email.assert_called_once()
        call_kwargs = mock_ses.send_email.call_args.kwargs
        self.assertEqual(
            call_kwargs["Destination"]["ToAddresses"],
            ["dev@example.com", "manager@example.com"],
        )
        self.assertIn("Html", call_kwargs["Message"]["Body"])
        self.assertIn("Error Summary", call_kwargs["Message"]["Body"]["Html"]["Data"])

    @patch("handler.ses_client")
    @patch.dict(os.environ, {"RECIPIENT_EMAILS": ""})
    def test_no_recipients_configured_skips_send(self, mock_ses):
        event = _sns_event(
            {"AlarmName": "sandbox-404-error-alarm", "StateChangeTime": ""}
        )

        handler.lambda_handler(event, MagicMock())

        mock_ses.send_email.assert_not_called()


if __name__ == "__main__":
    unittest.main()
