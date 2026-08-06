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

To add or remove a recipient:

1. Open a PR that updates the `default` value of the `error_notification_emails` variable in `infra/variables.tf`
   (or set the `TF_VAR_error_notification_emails` environment variable, as a JSON array, if overriding per environment).
2. Get the PR reviewed and merged like any other change.
3. The next `terraform apply` updates the Lambda's environment variables so the new list takes effect — no manual
   AWS Console steps or per-recipient email confirmation are required.

### What the Notification Email Looks Like

Each email has:
- A subject line naming the environment and the problem, e.g. `Production website error detected: server errors (5xx)`
- A short, plain-English body: what happened, when it happened, and the environment
- A plain link to the relevant CloudWatch log group so you can see the logs that triggered the alarm
- A clearly labeled "Technical details (for developers)" section at the end containing the raw alarm JSON, for anyone
  who needs to dig deeper

### Alert Response

When you receive an error notification email:
1. Click the "View the related logs" link to open the relevant CloudWatch log group directly
2. Use the timestamp in the email to narrow down the time range in the CloudWatch console
3. If you need the raw alarm details (metric name, trigger configuration, etc.), refer to the "Technical details" section at the bottom of the email

### Configurating Periods and Threshold

The alarm period (how frequently the metric is evaluated) and threshold (number of errors that trigger the alarm) can be manually adjusted in the AWS Console by:

1. Navigate to CloudWatch > Alarms
2. Find and select the alarm named `{environment}-5xx-error-alarm`
3. Click "Edit"
4. Under "Metric and conditions", you can modify:
   - The "Period" value (currently set to 60 seconds)
   - The "Threshold" value (currently set to 0)
5. Click "Update alarm" to save changes
