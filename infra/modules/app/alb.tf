module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 8.4.0"

  name = "${var.environment}-load-balancer"

  load_balancer_type = "application"
  security_groups    = [module.vpc.default_security_group_id]
  subnets            = module.vpc.private_subnets
  vpc_id             = module.vpc.vpc_id

  security_group_rules = {
    ingress_https = {
      type        = "ingress"
      from_port   = 443
      to_port     = 443
      protocol    = "TCP"
      description = "HTTPS traffic from CloudFront only"
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

  http_tcp_listeners = []

  https_listeners = [
    {
      port               = 443
      protocol          = "HTTPS"
      certificate_arn   = aws_acm_certificate.main.arn
      target_group_index = 0
      rules = [
        {
          priority = 1
          conditions = [
            {
              http_header = {
                http_header_name = "X-CloudFront-Origin"
                values = [var.cloudfront_origin_secret]
              }
            }
          ]
          actions = [
            {
              type = "forward"
              target_group_index = 0
            }
          ]
        },
        {
          priority = 2
          conditions = []
          actions = [
            {
              type = "fixed-response"
              fixed_response = {
                content_type = "text/plain"
                message_body = "Access denied"
                status_code = "403"
              }
            }
          ]
        }
      ]
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
    data.aws_ec2_managed_prefix_list.cloudfront,
    aws_acm_certificate.main,
    aws_acm_certificate_validation.main
  ]
}

# Get CloudFront IP ranges
data "aws_ec2_managed_prefix_list" "cloudfront" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}
