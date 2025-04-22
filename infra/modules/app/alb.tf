module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 8.4.0"

  name = "${var.environment}-load-balancer"

  load_balancer_type = "application"
  security_groups    = [module.vpc.default_security_group_id]
  subnets            = module.vpc.private_subnets
  vpc_id             = module.vpc.vpc_id

  security_group_rules = {
    ingress_http = {
      type        = "ingress"
      from_port   = 80
      to_port     = 80
      protocol    = "TCP"
      description = "HTTP traffic from CloudFront only"
      prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudfront.id]
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
      port               = 80
      protocol          = "HTTP"
      target_group_index = 0
    }
  ]

  https_listeners = []

  target_groups = [
    {
      backend_port     = local.container_port
      backend_protocol = "HTTP"
      target_type      = "ip"

      health_check = {
        healthy_threshold   = 3
        interval           = 30
        path               = "/"
        port               = "traffic-port"
        protocol          = "HTTP"
        timeout           = 5
        unhealthy_threshold = 3
      }
    }
  ]

  depends_on = [
    aws_vpc_endpoint.cloudfront,
    data.aws_ec2_managed_prefix_list.cloudfront
  ]
}

# Get CloudFront IP ranges
data "aws_ec2_managed_prefix_list" "cloudfront" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}
