# infra/modules/app/route53.tf

# Create a Route53 zone for your application
resource "aws_route53_zone" "main" {
  name = var.domain_name
}

# Create an A record for the domain pointing to the ALB
resource "aws_route53_record" "app" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = module.alb.lb_dns_name
    zone_id               = module.alb.lb_zone_id
    evaluate_target_health = true
  }
}

# Create a www subdomain that redirects to the apex domain
resource "aws_route53_record" "www" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = module.alb.lb_dns_name
    zone_id               = module.alb.lb_zone_id
    evaluate_target_health = true
  }
}
