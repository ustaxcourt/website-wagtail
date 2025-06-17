# An IAM role for the EventBridge Scheduler to assume, allowing it to run tasks on your behalf.
resource "aws_iam_role" "scheduler_for_ecs" {
  name = "${var.environment}-scheduler-for-ecs-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
      }
    ]
  })
}

# The policy that grants the scheduler permission to run an ECS task.
resource "aws_iam_policy" "scheduler_ecs_run_task" {
  name   = "${var.environment}-scheduler-ecs-run-task-policy"
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecs:RunTask"
        ]
        Effect   = "Allow"
        # Restrict this to the specific task definition you want it to be able to run
        Resource = aws_ecs_task_definition.this.arn
      },
      {
        # This permission is required for tasks that use an execution role
        Action = [
          "iam:PassRole"
        ]
        Effect   = "Allow"
        Resource = [
          aws_iam_role.this.arn, # The Task Execution Role
          aws_iam_role.ecs_task_role.arn # The Task Role
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "scheduler_ecs_run_task_attachment" {
  role       = aws_iam_role.scheduler_for_ecs.name
  policy_arn = aws_iam_policy.scheduler_ecs_run_task.arn
}


# A dedicated log group for the output of scheduled tasks
resource "aws_cloudwatch_log_group" "scheduled_task_logs" {
  name              = "/ecs/${var.environment}-scheduled-task-logs"
  retention_in_days = 14 # Keep logs for 14 days
}


# This resource defines the schedule and the target, including the command override.
resource "aws_scheduler_schedule" "run_daily_check" {
  name       = "${var.environment}-daily-management-command"
  group_name = "default"

  # Flexible schedule definition (e.g., daily at 2:00 AM UTC)
  schedule_expression = "cron(0 3 * * ? *)"

  # Ensures the schedule is created in an enabled state.
  state = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    # The ARN of the role the scheduler will use to run the task
    role_arn = aws_iam_role.scheduler_for_ecs.arn
    # The ARN of the ECS cluster where the task will run
    arn      = module.ecs.cluster_id

    ecs_parameters {
      # Use your EXISTING task definition
      task_definition_arn = aws_ecs_task_definition.this.arn
      launch_type         = "FARGATE"

      # Fargate tasks require a network configuration
      network_configuration {
        subnets          = module.vpc.private_subnets
        security_groups  = [aws_security_group.ecs_sg.id]
        assign_public_ip = false
      }
    }

    # THIS IS THE KEY PART: Here we override the default container command
    retry_policy {
      maximum_retry_attempts = 1
    }

    input = jsonencode({
      "overrides": {
        "containerOverrides": [
          {
            # The name must match the container name in your task definition
            "name": local.container_name,
            # The new command to execute instead of the one in the Dockerfile
            "command": [
              "python",
              "manage.py",
              "publish_scheduled"
            ],
            "logConfiguration": {
              "logDriver": "awslogs",
              "options": {
                "awslogs-group":         aws_cloudwatch_log_group.scheduled_task_logs.name,
                "awslogs-region":        "us-east-1",
                "awslogs-stream-prefix": "scheduled-task"
              }
            }
          }
        ]
      }
    })
  }
}
