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
        }

        subject, body = handler.build_email(alarm_message, "us-east-1")

        self.assertEqual(
            subject, "Production website error detected: Server errors (5xx)"
        )
        self.assertIn("What happened: This metric monitors for 5xx errors", body)
        self.assertIn("Environment: production", body)
        self.assertIn(
            "View the related logs: https://us-east-1.console.aws.amazon.com", body
        )
        self.assertIn("Technical details (for developers)", body)
        # Raw JSON must still be present, but only after the human-readable summary.
        self.assertLess(body.index("What happened"), body.index("Technical details"))

    def test_unrecognized_alarm_falls_back_to_generic_label(self):
        alarm_message = {"AlarmName": "train-some-other-alarm", "StateChangeTime": ""}

        subject, _ = handler.build_email(alarm_message, "us-east-1")

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
