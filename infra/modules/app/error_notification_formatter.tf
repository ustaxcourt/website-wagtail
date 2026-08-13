data "archive_file" "error_notification_formatter" {
  type        = "zip"
  source_file = "${path.module}/lambda/error_notification_formatter/handler.py"
  output_path = "${path.module}/lambda/error_notification_formatter.zip"
}

resource "aws_iam_role" "error_notification_formatter" {
  name = "${var.environment}-error-notification-formatter-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "error_notification_formatter_logs" {
  role       = aws_iam_role.error_notification_formatter.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "error_notification_formatter_ses" {
  name = "${var.environment}-error-notification-formatter-ses-policy"
  role = aws_iam_role.error_notification_formatter.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ses:SendEmail"
        Resource = "*"
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "error_notification_formatter" {
  name              = "/aws/lambda/${var.environment}-error-notification-formatter"
  retention_in_days = 7
}

resource "aws_lambda_function" "error_notification_formatter" {
  function_name    = "${var.environment}-error-notification-formatter"
  role             = aws_iam_role.error_notification_formatter.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = 30
  filename         = data.archive_file.error_notification_formatter.output_path
  source_code_hash = data.archive_file.error_notification_formatter.output_base64sha256

  depends_on = [aws_cloudwatch_log_group.error_notification_formatter]

  environment {
    variables = {
      SENDER_EMAIL       = "noreply@${var.domain_name}"
      RECIPIENT_EMAILS   = join(",", var.error_notification_emails)
      APP_LOG_GROUP_NAME = aws_cloudwatch_log_group.ecs_log_group.name
      RDS_LOG_GROUP_NAME = "/aws/rds/instance/${aws_db_instance.default.identifier}/postgresql"
    }
  }
}

resource "aws_lambda_permission" "error_notifications_invoke_formatter" {
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.error_notification_formatter.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.error_notifications.arn
}

resource "aws_sns_topic_subscription" "error_notification_formatter" {
  topic_arn = aws_sns_topic.error_notifications.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.error_notification_formatter.arn
}
