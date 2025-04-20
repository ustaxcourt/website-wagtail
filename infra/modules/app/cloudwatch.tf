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
          start       = "-P1D" # Last 24 hours
          end         = "P0D"  # Now
          query       = "SOURCE '${aws_cloudwatch_log_group.ecs_log_group.name}' | fields @timestamp, levelname, name\n| stats count(*) as events,\n         min(@timestamp) as firstSeen,\n         max(@timestamp) as lastSeen\n  by levelname, name\n| sort events desc\n"
          interactiveParameters = {
            logLevel  = {
              type = "string",
              column = "levelname"
            },
            component = {
              type = "string",
              column = "name"
            }
          }
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 12
        properties = {
          region      = "us-east-1"
          title       = "Detailed Log Messages"
          view        = "table"
          stacked     = false
          start       = "-P1D" # Last 24 hours
          end         = "P0D"  # Now
          query       = "SOURCE '${aws_cloudwatch_log_group.ecs_log_group.name}' | fields @timestamp, levelname, name, message, exc_info\n| filter levelname = '${interactiveParameters.logLevel.value}'\n| sort @timestamp desc\n| limit 1000"
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
            ["AWS/Logs", "IncomingLogEvents", "LogGroupName", aws_cloudwatch_log_group.ecs_log_group.name]
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
            ["AWS/Logs", "IncomingBytes", "LogGroupName", aws_cloudwatch_log_group.ecs_log_group.name]
          ]
          region = "us-east-1"
          title  = "Log Size"
          period = 300
        }
      }
    ]
  })
}

# Optional: Create CloudWatch Alarms for error logs
resource "aws_cloudwatch_metric_alarm" "error_logs_alarm" {
  alarm_name          = "high-error-rate-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ErrorCount"
  namespace           = "AWS/Logs"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This alarm triggers when there are more than 10 error logs in 5 minutes"

  dimensions = {
    LogGroupName = aws_cloudwatch_log_group.ecs_log_group.name
  }

  # Optional: Add SNS topic ARN if you want to send notifications
  # alarm_actions = [aws_sns_topic.alerts.arn]
}

# CloudWatch Log Metric Filter for ERROR level logs
resource "aws_cloudwatch_log_metric_filter" "error_logs" {
  name           = "error-logs-filter"
  pattern        = "{ $.levelname = \"ERROR\" }"
  log_group_name = aws_cloudwatch_log_group.ecs_log_group.name

  metric_transformation {
    name      = "ErrorCount"
    namespace = "AWS/Logs"
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
    namespace = "AWS/Logs"
    value     = "1"
  }
}
