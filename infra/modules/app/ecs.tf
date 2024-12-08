# resource "aws_iam_service_linked_role" "ecs" {
#   aws_service_name = "ecs.amazonaws.com"
# }

module "ecs" {
  # depends_on = [aws_iam_service_linked_role.ecs]

  source  = "terraform-aws-modules/ecs/aws"
  version = "~> 4.1.3"

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

resource "aws_secretsmanager_secret" "database_url_secret" {
  name        = "database-url"
  description = "Secret for the PostgreSQL database URL"
}

resource "aws_secretsmanager_secret_version" "database_url_secret_version" {
  secret_id = aws_secretsmanager_secret.database_url_secret.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql://${aws_db_instance.default.username}:${aws_db_instance.default.password}@${aws_db_instance.default.endpoint}/postgres"
  })
}

resource "aws_ecs_task_definition" "this" {
  container_definitions = jsonencode([{
    environment: [],
    secrets: [
      {
        name = "DATABASE_URL",
        valueFrom = "${aws_secretsmanager_secret.database_url_secret.arn}:DATABASE_URL::"
      }
    ],
    essential    = true,
    image        = docker_registry_image.this.name,
    name         = local.container_name,
    portMappings = [{ containerPort = local.container_port }],
    healthCheck = {
      "command"     = ["CMD", "curl", "-f", "http://localhost:${local.container_port}"]
      "interval"    = 30 # check every 30 seconds
      "retries"     = 3  # retry 3 times before marking as unhealthy
      "startPeriod" = 10 # initial delay before starting health checks
      "timeout"     = 5  # health check timeout in seconds
    }
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs_log_group.name, # Reference the CloudWatch log group
        "awslogs-region"        = "us-east-1",                                 # Your AWS region
        "awslogs-stream-prefix" = "my-fargate-service"                         # Log stream prefix
      }
    }
  }])
  cpu                      = 512 # 1 vCPU
  execution_role_arn       = aws_iam_role.this.arn
  family                   = "${var.environment}-website-tasks"
  memory                   = 1024 # wagtail recommended minimum
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
}


resource "aws_ecs_service" "this" {
  # depends_on = [aws_iam_service_linked_role.ecs]

  cluster         = module.ecs.cluster_id
  desired_count   = 0
  launch_type     = "FARGATE"
  name            = "${var.environment}-website-service"
  task_definition = aws_ecs_task_definition.this.arn

  lifecycle {
    // we ignore both of these because later in the github actions pipeline,
    // we manually run an ECS update after the migration scripts have run
    // so that we do not deploy new versions of the app before the migration scripts
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
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow ECS tasks to communicate with the RDS instance
  # TODO: might be better to scope it to just postgres port and maybe even point to rds security group
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
      aws_secretsmanager_secret.database_url_secret.arn
    ]
  }
}
