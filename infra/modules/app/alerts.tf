resource "aws_cloudwatch_log_metric_filter" "error_500_filter" {
  name           = "${var.environment}-5xx-error-filter"
  pattern        = "{ $.status_code >= 500 && $.status_code < 600 }"
  log_group_name = aws_cloudwatch_log_group.ecs_log_group.name

  metric_transformation {
    name      = "5xxErrorCount"
    namespace = "WebsiteErrors"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "error_500_alarm" {
  alarm_name          = "${var.environment}-5xx-error-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "5xxErrorCount"
  namespace           = "WebsiteErrors"
  period             = "60"
  statistic          = "Sum"
  threshold          = "1"
  alarm_description  = "This metric monitors for 5xx errors in the website logs"
  alarm_actions      = [aws_sns_topic.error_notifications.arn]
}

resource "aws_sns_topic" "error_notifications" {
  name = "${var.environment}-error-notifications"
}

resource "aws_sns_topic_policy" "error_notifications" {
  arn = aws_sns_topic.error_notifications.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.error_notifications.arn
      }
    ]
  })
}
