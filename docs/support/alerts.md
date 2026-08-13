## Website Error Monitoring and Alerts

The website infrastructure includes CloudWatch monitoring and SNS notifications for critical errors, particularly 5xx server errors that could indicate system-wide issues.

### Alert Configuration

The monitoring system is configured to:
- Track 5xx errors (status codes 500-599), noisy 404s, and RDS `ERROR`/`FATAL`/`PANIC` log lines
- Trigger an alarm when the configured threshold is crossed
- Publish to an SNS topic (`{environment}-error-notifications`), which invokes the `error-notification-formatter` Lambda
  (see [infra/modules/app/error_notification_formatter.tf](/infra/modules/app/error_notification_formatter.tf) and
  [infra/modules/app/lambda/error_notification_formatter/handler.py](/infra/modules/app/lambda/error_notification_formatter/handler.py))
- The Lambda turns the raw CloudWatch alarm payload into a human-readable email and sends it via SES

### Managing Error Notification Recipients

Recipients are **not** managed by subscribing individually in the AWS Console. Instead, they're defined in a single
source-controlled place: the `error_notification_emails` Terraform variable
(declared in [infra/variables.tf](/infra/variables.tf) and [infra/modules/app/variables.tf](/infra/modules/app/variables.tf)).

Per-environment values come from the `ERROR_NOTIFICATION_EMAILS` entry in that environment's `website_secrets` AWS
Secrets Manager secret — a comma-separated list of email addresses (e.g. `dev@example.com,manager@example.com`).
[infra/setup.sh](/infra/setup.sh) converts it into the `error_notification_emails` Terraform variable at deploy time.
If that secret key is unset for an environment, the variable falls back to its (empty) default in `infra/variables.tf`.

To add or remove a recipient for an environment:

1. Update the `ERROR_NOTIFICATION_EMAILS` key in that environment's `website_secrets` secret (AWS Secrets Manager).
2. Re-run the deploy (or the next scheduled deploy will pick it up).

No manual AWS Console SNS subscription or per-recipient email confirmation is required.

#### Step-by-Step: Add a Recipient

1. Open AWS Secrets Manager in the target environment account.
2. Open the secret named `website_secrets`.
3. Edit the `ERROR_NOTIFICATION_EMAILS` entry.
4. Set it to a comma-separated list of recipients, for example:
   `samuel.egwurube.ctr@ustaxcourt.gov,somraj.subedi.ctr@ustaxcourt.gov`
5. Save the secret.
6. Redeploy that environment so [infra/setup.sh](/infra/setup.sh) can read the updated secret and pass it into Terraform.
7. Confirm the deploy completed successfully. The Lambda environment variable `RECIPIENT_EMAILS` will then be rebuilt from that value.

Notes:
- Do not add recipients by editing the SNS topic in the AWS Console. The SNS topic invokes the formatter Lambda, and the Lambda sends the email through SES.
- There is no separate email confirmation flow for recipients.
- If an address is missing from `ERROR_NOTIFICATION_EMAILS` at deploy time, that address will not receive notifications even if the alarm, SNS topic, and Lambda are all working.

### What the Notification Email Looks Like

Each email has:
- A subject line naming the environment and the problem, e.g. `Production website error detected: server errors (5xx)`
- An `Error Summary` section with the actual CloudWatch alarm reason, when it fired, and the environment
- A direct link to the relevant CloudWatch log events view
- Suggested filter guidance and time window information to help locate the triggering log lines quickly
- A clearly labeled "Technical details (for developers)" section at the end containing the raw alarm JSON, for anyone
  who needs to dig deeper

### Alert Response

When you receive an error notification email:
1. Click the "Open matching log events" link to open the relevant CloudWatch log events view
2. Apply the suggested filter pattern from the email if CloudWatch does not preserve it automatically
3. Use the suggested time window in the email to narrow the results in the CloudWatch console
4. If you need the raw alarm details (metric name, trigger configuration, etc.), refer to the "Technical details" section at the bottom of the email

### Configurating Periods and Threshold

The alarm period (how frequently the metric is evaluated) and threshold (number of errors that trigger the alarm) can be manually adjusted in the AWS Console by:

1. Navigate to CloudWatch > Alarms
2. Find and select the alarm named `{environment}-5xx-error-alarm`
3. Click "Edit"
4. Under "Metric and conditions", you can modify:
  - The "Period" value
  - The "Threshold" value
5. Click "Update alarm" to save changes
