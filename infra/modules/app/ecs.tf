# resource "aws_iam_service_linked_role" "ecs" {
#   aws_service_name = "ecs.amazonaws.com"
# }

module "ecs" {
  # depends_on = [aws_iam_service_linked_role.ecs]

  source  = "terraform-aws-modules/ecs/aws"
  version = "5.12.1"

  cluster_name = "${var.environment}-website-cluster"

  # * Allocate 20% capacity to FARGATE and then split
  # * the remaining 80% capacity 50/50 between FARGATE
  # * and FARGATE_SPOT.
  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        base   = 0
        weight = 100
      }
    }
  }
}

resource "aws_secretsmanager_secret" "ecs_task_secrets" {
  name_prefix = "ecs-task-secrets-"
  description = "Secrets used for the ecs task to prevent easy access to the secrets via aws cli commands"
}

resource "aws_secretsmanager_secret_version" "ecs_task_secrets_version" {
  secret_id = aws_secretsmanager_secret.ecs_task_secrets.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql://${aws_db_instance.default.username}:${aws_db_instance.default.password}@${aws_db_instance.default.endpoint}/postgres"
    SECRET_KEY = var.secret_key
    SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = var.social_auth_azuread_tenant_oauth2_secret
  })
}

# Define a new IAM role for the ECS task
resource "aws_iam_role" "ecs_task_role" {
  name               = "${var.environment}-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.this.json
}

# Attach the S3 full access policy to the ECS task role
resource "aws_iam_role_policy_attachment" "ecs_task_s3_access" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# Add CloudFront invalidation policy to the ECS task role
resource "aws_iam_role_policy" "ecs_task_cloudfront_invalidation" {
  name = "${var.environment}-ecs-task-cloudfront-invalidation"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation"
        ]
        Resource = [
          "arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/${aws_cloudfront_distribution.app.id}"
        ]
      }
    ]
  })
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Updated ECS task definition
resource "aws_ecs_task_definition" "this" {
  container_definitions = jsonencode([{
    environment: [
      {
        name = "DOMAIN_NAME",
        value = var.domain_name
      },
      {
        name = "AWS_STORAGE_BUCKET_NAME",
        value = aws_s3_bucket.private_bucket.id
      },
      {
        name = "DJANGO_SETTINGS_MODULE",
        value = "app.settings.${var.environment}"
      },
      {
        name = "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY",
        value = var.social_auth_azuread_tenant_oauth2_key
      },
      {
        name = "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID",
        value = var.social_auth_azuread_tenant_oauth2_tenant_id
      },
      {
        name = "CLOUDFRONT_DISTRIBUTION_ID",
        value = aws_cloudfront_distribution.app.id
      }
    ],
    secrets: [
      {
        name = "DATABASE_URL",
        valueFrom = "${aws_secretsmanager_secret.ecs_task_secrets.arn}:DATABASE_URL::"
      },
      {
        name = "SECRET_KEY",
        valueFrom = "${aws_secretsmanager_secret.ecs_task_secrets.arn}:SECRET_KEY::"
      },
      {
        name = "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET",
        valueFrom = "${aws_secretsmanager_secret.ecs_task_secrets.arn}:SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET::"
      },
    ],

    essential    = true,
    image        = docker_registry_image.this.name,
    name         = local.container_name,
    portMappings = [{ containerPort = local.container_port }],
    healthCheck = {
      "command"     = ["CMD", "curl", "-f", "http://localhost:${local.container_port}"]
      "interval"    = 30 # check every 30 seconds
      "retries"     = 3  # retry 3 times before marking as unhealthy
      "startPeriod" = 30 # initial delay before starting health checks
      "timeout"     = 5  # health check timeout in seconds
    }
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs_log_group.name,
        "awslogs-region"        = "us-east-1",
        "awslogs-stream-prefix" = "wagtail-fargate-service"
      }
    }
  }])
  cpu                      = local.cpu_units
  execution_role_arn       = aws_iam_role.this.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  family                   = "${var.environment}-website-tasks"
  memory                   = local.memory_mb
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
}

resource "aws_ecs_service" "this" {
  cluster         = module.ecs.cluster_id
  desired_count   = 0
  launch_type     = "FARGATE"
  name            = "${var.environment}-website-service"
  task_definition = aws_ecs_task_definition.this.arn

  # Enable the ECS deployment circuit breaker for rollbacks
  deployment_controller {
    type = "ECS"
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  lifecycle {
    ignore_changes = [
      task_definition,
      desired_count
    ]
  }

  load_balancer {
    container_name   = local.container_name
    container_port   = local.container_port
    target_group_arn = module.alb.target_group_arns[0]
  }

  network_configuration {
    security_groups = [aws_security_group.ecs_sg.id]
    subnets         = module.vpc.private_subnets
  }
}

# Security group for ECS tasks
resource "aws_security_group" "ecs_sg" {
  name        = "${var.environment}-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    security_groups = [module.alb.security_group_id]  # Allow traffic from ALB security group
  }

  # Allow ECS tasks to communicate with the RDS instance
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/${var.environment}-website-logs"
  retention_in_days = 7 # You can modify this as needed
}

# * Step 6 - Create our ECS Task Definition
data "aws_iam_policy_document" "this" {
  version = "2012-10-17"

  statement {
    actions = [
      "sts:AssumeRole",
    ]
    effect = "Allow"

    principals {
      identifiers = ["ecs-tasks.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_iam_role" "this" { assume_role_policy = data.aws_iam_policy_document.this.json }

resource "aws_iam_role_policy_attachment" "this" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  role       = aws_iam_role.this.name
}

resource "aws_iam_role_policy_attachment" "ecs_cloudwatch_logs" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_iam_role_policy" "ecs_task_secrets_access" {
  name   = "ecs_task_secrets_access"
  role   = aws_iam_role.this.name
  policy = data.aws_iam_policy_document.ecs_task_secrets_policy.json
}

data "aws_iam_policy_document" "ecs_task_secrets_policy" {
  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue"
    ]

    resources = [
      aws_secretsmanager_secret.ecs_task_secrets.arn
    ]
  }
}
