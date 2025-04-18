module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 8.4.0"

  name = "${var.environment}-load-balancer"

  load_balancer_type = "application"
  security_groups    = [module.vpc.default_security_group_id]
  subnets            = module.vpc.private_subnets  # ALB in private subnets
  vpc_id             = module.vpc.vpc_id

  security_group_rules = {
    ingress_http = {
      type        = "ingress"
      from_port   = 80
      to_port     = 80
      protocol    = "TCP"
      description = "HTTP traffic"
      cidr_blocks = ["0.0.0.0/0"]
    }
    ingress_https = {
      type        = "ingress"
      from_port   = 443
      to_port     = 443
      protocol    = "TCP"
      description = "HTTPS traffic"
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
      port        = 80
      protocol    = "HTTP"
      action_type = "redirect"
      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  ]

  https_listeners = [
    {
      port               = 443
      protocol          = "HTTPS"
      certificate_arn   = aws_acm_certificate.main.arn
      target_group_index = 0
    }
  ]

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
    aws_acm_certificate.main,
    aws_acm_certificate_validation.main
  ]
}
