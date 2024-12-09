module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 8.4.0"

  name = "${var.environment}-load-balancer"

  load_balancer_type = "application"
  security_groups    = [module.vpc.default_security_group_id]
  subnets            = module.vpc.public_subnets
  vpc_id             = module.vpc.vpc_id

  security_group_rules = {
    ingress_all_http = {
      type        = "ingress"
      from_port   = 80
      to_port     = 80
      protocol    = "TCP"
      description = "HTTP web traffic"
      cidr_blocks = ["0.0.0.0/0"]
    }

    egress_all = {
      type        = "egress"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  http_tcp_listeners = [
    {
      # ! Defaults to "forward" action for "target group"
      # ! at index = 0 in "the target_groups" input below.
      port               = 80
      protocol           = "HTTP"
      target_group_index = 0
    }
  ]

  target_groups = [
    {
      backend_port     = local.container_port
      backend_protocol = "HTTP"
      target_type      = "ip"

      health_check = {
        healthy_threshold   = 3              # Increase the number of consecutive successful health checks before considering as healthy
        interval            = 30             # Health check interval in seconds
        path                = "/"            # Adjust if you have a custom health check endpoint
        port                = "traffic-port" # Port to use for health checks (typically "traffic-port")
        protocol            = "HTTP"         # Use HTTP for health checks
        timeout             = 5              # Timeout for health check
        unhealthy_threshold = 3              # Number of consecutive failed health checks before considering as unhealthy
      }
    }
  ]
}
