resource "aws_cloudwatch_dashboard" "log_dashboard" {
  dashboard_name = "website-logs-dashboard"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "log"
        x      = 0
        y      = 0
        width  = 24
        height = 6
        properties = {
          region      = "us-east-1"
          title       = "Log Summary by Level and Component"
          view        = "table"
          stacked     = false
          query       = <<EOT
SOURCE '${aws_cloudwatch_log_group.ecs_log_group.name}' | fields @timestamp, levelname, name
| stats  count(*)       as events,
         min(@timestamp) as firstSeen,
         max(@timestamp) as lastSeen
  by levelname, name
| sort events desc
EOT
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 6
        properties = {
          region      = "us-east-1"
          title       = "5xx Error Logs"
          view        = "table"
          stacked     = false
          query       = <<EOT
SOURCE '${aws_cloudwatch_log_group.ecs_log_group.name}'
| filter status_code >= 500 and status_code < 600
| fields @timestamp, status_code, message, path
| sort @timestamp desc
EOT
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        properties = {
          region      = "us-east-1"
          title       = "404 Not Found Errors"
          view        = "table"
          stacked     = false
          query       = <<EOT
SOURCE '${aws_cloudwatch_log_group.ecs_log_group.name}'
| filter status_code = 404
| fields @timestamp, status_code, message, path
| sort @timestamp desc
| limit 40
EOT
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 18
        width  = 12
        height = 6
        properties = {
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/Logs", "IncomingLogEvents", "LogGroupName", "${aws_cloudwatch_log_group.ecs_log_group.name}"]
          ]
          region = "us-east-1"
          title  = "Log Volume"
          period = 300
        }
      },

      {
        type   = "metric"
        x      = 12
        y      = 18
        width  = 12
        height = 6
        properties = {
          view    = "timeSeries"
          stacked = true
          metrics = [
            ["AWS/Logs", "IncomingBytes", "LogGroupName", "${aws_cloudwatch_log_group.ecs_log_group.name}"]
          ]
          region = "us-east-1"
          title  = "Log Size"
          period = 300
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 24
        width  = 24
        height = 6
        properties = {
          region      = "us-east-1"
          title       = "RDS Error Logs"
          view        = "table"
          stacked     = false
          query       = <<EOT
SOURCE '/aws/rds/instance/${aws_db_instance.default.identifier}/postgresql'
| filter @message like /ERROR|FATAL|PANIC/
| fields @timestamp, @message
| sort @timestamp desc
| limit 40
EOT
        }
      }
    ]
  })
}

# CloudWatch Log Metric Filter for ERROR level logs
resource "aws_cloudwatch_log_metric_filter" "error_logs" {
  name           = "error-logs-filter"
  pattern        = "{ $.levelname = \"ERROR\" }"
  log_group_name = aws_cloudwatch_log_group.ecs_log_group.name

  metric_transformation {
    name      = "ErrorCount"
    namespace = "CustomMetrics/Logs"
    value     = "1"
  }
}

# CloudWatch Log Metric Filter for WARNING level logs
resource "aws_cloudwatch_log_metric_filter" "warning_logs" {
  name           = "warning-logs-filter"
  pattern        = "{ $.levelname = \"WARNING\" }"
  log_group_name = aws_cloudwatch_log_group.ecs_log_group.name

  metric_transformation {
    name      = "WarningCount"
    namespace = "CustomMetrics/Logs"
    value     = "1"
  }
}

# CloudWatch Alarm for ERROR logs
resource "aws_cloudwatch_metric_alarm" "error_logs_alarm" {
  alarm_name          = "high-error-rate-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ErrorCount"
  namespace           = "CustomMetrics/Logs"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This alarm triggers when there are more than 10 error logs in 5 minutes"

  dimensions = {
    LogGroupName = aws_cloudwatch_log_group.ecs_log_group.name
  }
}
