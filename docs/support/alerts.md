## Website Error Monitoring and Alerts

The website infrastructure includes CloudWatch monitoring and SNS notifications for critical errors, particularly 5xx server errors that could indicate system-wide issues.

### Alert Configuration

The monitoring system is configured to:
- Track 5xx errors (status codes 500-599) in application logs
- Trigger an alarm immediately when any 5xx error occurs (threshold > 0)
- Send notifications via SNS (Simple Notification Service) when alarms trigger

### Subscribing to Error Notifications

To receive 5xx error notifications:

1. Navigate to the AWS SNS Console
2. Find the SNS topic named `{environment}-error-notifications` (e.g. `production-error-notifications`)
3. Click "Create subscription"
4. Choose your preferred notification method:
   - Email: Select "Email" protocol and enter your email address
   - SMS: Select "SMS" protocol and enter your phone number
   - HTTP/HTTPS: Select appropriate protocol and enter your endpoint URL
   - AWS Lambda: Select "AWS Lambda" and choose your function
5. Click "Create subscription"
6. For email subscriptions, confirm by clicking the link in the verification email

You can add multiple subscriptions to the same topic to notify different people or systems through different channels.

### Alert Response

When you receive a 5xx error notification email:
1. Click the alarm link in the email notification to open the CloudWatch alarm directly
2. On the alarm page, click the "View" button, then the "Related logs" entry, then click the log group
3. This should open cloudwatch with all the filters already setup so you can view the related logs that triggered the alarm.
