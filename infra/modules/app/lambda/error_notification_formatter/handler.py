"""Reformats raw CloudWatch alarm SNS messages into human-readable emails and sends them via SES."""

import json
import os
from datetime import datetime

import boto3

ses_client = boto3.client("ses")

# Maps the alarm name suffix (set in alerts.tf) to a plain-English description
# and the env var holding the log group the alarm's logs live in.
ALARM_TYPES = {
    "5xx-error-alarm": {
        "label": "server errors (5xx)",
        "log_group_env": "APP_LOG_GROUP_NAME",
    },
    "404-error-alarm": {
        "label": "a high volume of page-not-found errors (404)",
        "log_group_env": "APP_LOG_GROUP_NAME",
    },
    "rds-error-alarm": {
        "label": "database errors",
        "log_group_env": "RDS_LOG_GROUP_NAME",
    },
}
DEFAULT_ALARM_TYPE = {"label": "an error", "log_group_env": "APP_LOG_GROUP_NAME"}


def _alarm_type(alarm_name: str) -> dict:
    for suffix, info in ALARM_TYPES.items():
        if alarm_name.endswith(suffix):
            return info
    return DEFAULT_ALARM_TYPE


def _environment_from_alarm(alarm_name: str) -> str:
    return alarm_name.split("-", 1)[0]


def _format_timestamp(iso_timestamp: str) -> str:
    try:
        parsed = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        return parsed.strftime("%B %d, %Y at %I:%M %p UTC")
    except (ValueError, AttributeError):
        return iso_timestamp or "unknown time"


def _log_group_url(region: str, log_group_name: str) -> str:
    # CloudWatch's console requires "/" in log group names to be double-encoded.
    encoded_group = log_group_name.replace("/", "$252F")
    return (
        f"https://{region}.console.aws.amazon.com/cloudwatch/home"
        f"?region={region}#logsV2:log-groups/log-group/{encoded_group}"
    )


def build_email(alarm_message: dict, region: str) -> tuple[str, str]:
    alarm_name = alarm_message.get("AlarmName", "unknown-alarm")
    environment = _environment_from_alarm(alarm_name)
    alarm_type = _alarm_type(alarm_name)
    when = _format_timestamp(alarm_message.get("StateChangeTime", ""))
    description = alarm_message.get("AlarmDescription") or "No description provided."

    subject = f"{environment.title()} website error detected: {alarm_type['label'].capitalize()}"

    lines = [
        f"What happened: {description}",
        f"When: {when}",
        f"Environment: {environment}",
        "",
    ]

    log_group_name = os.environ.get(alarm_type["log_group_env"], "")
    if log_group_name:
        lines.append(f"View the related logs: {_log_group_url(region, log_group_name)}")
        lines.append("")

    lines.append("-" * 60)
    lines.append("Technical details (for developers)")
    lines.append("-" * 60)
    lines.append(json.dumps(alarm_message, indent=2))

    return subject, "\n".join(lines)


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
        subject, body = build_email(alarm_message, region)

        ses_client.send_email(
            Source=sender,
            Destination={"ToAddresses": recipients},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
