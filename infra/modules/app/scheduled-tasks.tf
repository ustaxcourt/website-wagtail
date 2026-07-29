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


resource "aws_scheduler_schedule" "run_daily_check" {
  name       = "${var.environment}-daily-management-command"
  group_name = "default"

  schedule_expression = "cron(0 * * * ? *)"

  lifecycle {
    ignore_changes = [schedule_expression]
  }

  state = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    role_arn = aws_iam_role.scheduler_for_ecs.arn
    arn      = module.ecs.cluster_id

    ecs_parameters {
      # Use EXISTING task definition
      task_definition_arn = aws_ecs_task_definition.this.arn
      launch_type         = "FARGATE"

      network_configuration {
        subnets          = module.vpc.private_subnets
        security_groups  = [aws_security_group.ecs_sg.id]
        assign_public_ip = false
      }
    }

    retry_policy {
      maximum_retry_attempts = 1
    }

    input = jsonencode({
      "containerOverrides": [
        {
          # The name must match the container name in your task definition
          "name": local.container_name,
          # The new command to execute instead of the one in the Dockerfile
          "command": [
            "python",
            "manage.py",
            "publish_scheduled"
          ]
        }
      ]
    })
  }
}

resource "aws_scheduler_schedule" "run_linkcheck" {
  name       = "${var.environment}-linkcheck-command"
  group_name = "default"

  schedule_expression = "cron(0 0 ? * SUN *)"

  schedule_expression_timezone = "America/New_York"

  lifecycle {
    ignore_changes = [schedule_expression]
  }

  state = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    role_arn = aws_iam_role.scheduler_for_ecs.arn
    arn      = module.ecs.cluster_id

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.this.arn
      launch_type         = "FARGATE"

      network_configuration {
        subnets          = module.vpc.private_subnets
        security_groups  = [aws_security_group.ecs_sg.id]
        assign_public_ip = false
      }
    }

    retry_policy {
      maximum_retry_attempts = 1
    }

    input = jsonencode({
      "containerOverrides": [
        {
          "name": local.container_name,
          "command": [
            "python",
            "manage.py",
            "linkcheck"
          ]
        }
      ]
    })
  }
}

resource "aws_scheduler_schedule" "run_send_moderator_digest" {
  count      = contains(var.email_scheduler_enabled_environments, var.environment) ? 1 : 0
  name       = "${var.environment}-send_moderator_digest-command"
  group_name = "default"

  schedule_expression = "cron(0 14 ? * MON-FRI *)"

  schedule_expression_timezone = "America/New_York"

  lifecycle {
    ignore_changes = [schedule_expression]
  }

  state = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    role_arn = aws_iam_role.scheduler_for_ecs.arn
    arn      = module.ecs.cluster_id

    ecs_parameters {
      # Use EXISTING task definition
      task_definition_arn = aws_ecs_task_definition.this.arn
      launch_type         = "FARGATE"

      network_configuration {
        subnets          = module.vpc.private_subnets
        security_groups  = [aws_security_group.ecs_sg.id]
        assign_public_ip = false
      }
    }

    retry_policy {
      maximum_retry_attempts = 1
    }

    input = jsonencode({
      "containerOverrides": [
        {
          # The name must match the container name in your task definition
          "name": local.container_name,
          # The new command to execute instead of the one in the Dockerfile
          "command": [
            "python",
            "manage.py",
            "send_moderator_digest"
          ]
        }
      ]
    })
  }
}
