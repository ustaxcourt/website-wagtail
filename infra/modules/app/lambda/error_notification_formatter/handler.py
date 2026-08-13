"""Reformats raw CloudWatch alarm SNS messages into human-readable emails and sends them via SES."""

import html
import json
import os
from datetime import datetime

import boto3

ses_client = boto3.client("ses", region_name=os.environ.get("AWS_REGION", "us-east-1"))

# Maps the alarm name suffix (set in alerts.tf) to a plain-English description
# and the env var holding the log group the alarm's logs live in.
ALARM_TYPES = {
    "5xx-error-alarm": {
        "label": "server errors (5xx)",
        "log_group_env": "APP_LOG_GROUP_NAME",
        "filter_pattern": "{ $.status_code >= 500 && $.status_code < 600 }",
    },
    "404-error-alarm": {
        "label": "a high volume of page-not-found errors (404)",
        "log_group_env": "APP_LOG_GROUP_NAME",
        "filter_pattern": "{ $.status_code = 404 }",
    },
    "rds-error-alarm": {
        "label": "database errors",
        "log_group_env": "RDS_LOG_GROUP_NAME",
        "filter_pattern": "ERROR OR FATAL OR PANIC",
    },
}
DEFAULT_ALARM_TYPE = {
    "label": "an error",
    "log_group_env": "APP_LOG_GROUP_NAME",
    "filter_pattern": "",
}


def _alarm_type(alarm_name: str) -> dict:
    for suffix, info in ALARM_TYPES.items():
        if alarm_name.endswith(suffix):
            return info
    return DEFAULT_ALARM_TYPE


def _environment_from_alarm(alarm_name: str) -> str:
    return alarm_name.split("-", 1)[0]


def _format_timestamp(iso_timestamp: str) -> str:
    if not iso_timestamp:
        return "unknown time"
    normalized = iso_timestamp.replace("Z", "+00:00")
    # Handle offsets like "+0000" / "-0700" by converting to "+00:00" / "-07:00".
    if len(normalized) >= 5 and normalized[-5] in "+-" and normalized[-3] != ":":
        normalized = normalized[:-2] + ":" + normalized[-2:]
    try:
        parsed = datetime.fromisoformat(normalized)
        return parsed.strftime("%B %d, %Y at %I:%M %p UTC")
    except (ValueError, AttributeError):
        return iso_timestamp


def _log_group_url(region: str, log_group_name: str) -> str:
    # CloudWatch's console requires "/" in log group names to be double-encoded.
    encoded_group = log_group_name.replace("/", "$252F")
    return (
        f"https://{region}.console.aws.amazon.com/cloudwatch/home"
        f"?region={region}#logsV2:log-groups/log-group/{encoded_group}"
    )


def _log_events_url(region: str, log_group_name: str) -> str:
    encoded_group = log_group_name.replace("/", "$252F")
    return (
        f"https://{region}.console.aws.amazon.com/cloudwatch/home"
        f"?region={region}#logsV2:log-groups/log-group/{encoded_group}/log-events"
    )


def _alarm_reason(alarm_message: dict) -> str:
    return (
        alarm_message.get("NewStateReason")
        or alarm_message.get("StateReason")
        or alarm_message.get("AlarmDescription")
        or "No details provided."
    )


def _alarm_window(alarm_message: dict) -> tuple[str, str] | None:
    trigger = alarm_message.get("Trigger") or {}
    try:
        period_seconds = int(trigger.get("Period", 0))
        evaluation_periods = int(trigger.get("EvaluationPeriods", 1))
    except (TypeError, ValueError):
        return None

    state_change_time = alarm_message.get("StateChangeTime", "")
    if not state_change_time or period_seconds <= 0 or evaluation_periods <= 0:
        return None

    normalized = state_change_time.replace("Z", "+00:00")
    if len(normalized) >= 5 and normalized[-5] in "+-" and normalized[-3] != ":":
        normalized = normalized[:-2] + ":" + normalized[-2:]

    try:
        end = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    total_seconds = period_seconds * evaluation_periods
    start = end.timestamp() - total_seconds
    start_display = datetime.fromtimestamp(start, tz=end.tzinfo).strftime(
        "%B %d, %Y at %I:%M %p UTC"
    )
    end_display = end.strftime("%B %d, %Y at %I:%M %p UTC")
    return start_display, end_display


def build_email(alarm_message: dict, region: str) -> tuple[str, str, str]:
    alarm_name = alarm_message.get("AlarmName", "unknown-alarm")
    environment = _environment_from_alarm(alarm_name)
    alarm_type = _alarm_type(alarm_name)
    when = _format_timestamp(alarm_message.get("StateChangeTime", ""))
    reason = _alarm_reason(alarm_message)

    env_display = environment.upper() if environment in {"qa"} else environment.title()
    subject = (
        f"{env_display} website error detected: {alarm_type['label'].capitalize()}"
    )

    text_lines = [
        "Error Summary",
        "",
        f"What happened: {reason}",
        f"When: {when}",
        f"Environment: {environment}",
        "",
    ]

    html_lines = [
        "<h2>Error Summary</h2>",
        f"<p><strong>What happened:</strong> {html.escape(reason)}</p>",
        f"<p><strong>When:</strong> {html.escape(when)}</p>",
        f"<p><strong>Environment:</strong> {html.escape(environment)}</p>",
    ]

    log_group_name = os.environ.get(alarm_type["log_group_env"], "")
    if log_group_name:
        log_events_url = _log_events_url(region, log_group_name)
        text_lines.append(f"Open matching log events: {log_events_url}")
        html_lines.append(
            f'<p><strong>Open matching log events:</strong> <a href="{html.escape(log_events_url)}">{html.escape(log_events_url)}</a></p>'
        )
        if alarm_type["filter_pattern"]:
            text_lines.append(
                f"Suggested filter pattern: {alarm_type['filter_pattern']}"
            )
            html_lines.append(
                f"<p><strong>Suggested filter pattern:</strong> {html.escape(alarm_type['filter_pattern'])}</p>"
            )

        alarm_window = _alarm_window(alarm_message)
        if alarm_window:
            start_display, end_display = alarm_window
            text_lines.append(
                f"Suggested time window: {start_display} to {end_display}"
            )
            html_lines.append(
                f"<p><strong>Suggested time window:</strong> {html.escape(start_display)} to {html.escape(end_display)}</p>"
            )

        text_lines.append(f"Log group: {log_group_name}")
        text_lines.append("")
        html_lines.append(
            f"<p><strong>Log group:</strong> {html.escape(log_group_name)}</p>"
        )

    technical_details = json.dumps(alarm_message, indent=2)
    text_lines.append("Technical details (for developers)")
    text_lines.append(technical_details)
    html_lines.append(
        "<p><strong><u>Technical details (for developers)</u></strong></p>"
    )
    html_lines.append(f"<pre>{html.escape(technical_details)}</pre>")

    return subject, "\n".join(text_lines), "\n".join(html_lines)


def lambda_handler(event, context):
    region = os.environ.get("AWS_REGION", "us-east-1")
    sender = os.environ["SENDER_EMAIL"]
    recipients = [
        address.strip()
        for address in os.environ.get("RECIPIENT_EMAILS", "").split(",")
        if address.strip()
    ]

    if not recipients:
        print("No error notification recipients configured; skipping email.")
        return

    for record in event.get("Records", []):
        alarm_message = json.loads(record["Sns"]["Message"])
        subject, text_body, html_body = build_email(alarm_message, region)

        ses_client.send_email(
            Source=sender,
            Destination={"ToAddresses": recipients},
            Message={
                "Subject": {"Data": subject},
                "Body": {
                    "Text": {"Data": text_body},
                    "Html": {"Data": html_body},
                },
            },
        )
