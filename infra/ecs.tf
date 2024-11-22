
module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "~> 4.1.3"

  cluster_name = "website-cluster"

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



resource "aws_ecs_task_definition" "this" {
  container_definitions = jsonencode([{
    environment : [
      { name = "DATABASE_URL", value = "postgresql://${aws_db_instance.default.username}:${aws_db_instance.default.password}@${aws_db_instance.default.endpoint}/postgres" }
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
  family                   = "website-tasks"
  memory                   = 1024 # wagtail recommended minimum
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
}


resource "aws_ecs_service" "this" {
  cluster         = module.ecs.cluster_id
  desired_count   = 1
  launch_type     = "FARGATE"
  name            = "website-service"
  task_definition = aws_ecs_task_definition.this.arn

  lifecycle {
    ignore_changes = [desired_count]
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
  name        = "ecs-sg"
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
  name              = "/ecs/website-logs"
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
