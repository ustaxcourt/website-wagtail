# infra/modules/app/route53.tf

data "aws_route53_zone" "main" {
  name = var.domain_name
}

# Create an A record for the domain pointing to CloudFront
resource "aws_route53_record" "app" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                  = aws_cloudfront_distribution.app.domain_name
    zone_id               = aws_cloudfront_distribution.app.hosted_zone_id
    evaluate_target_health = false
  }
}

# Create a www subdomain that redirects to the apex domain
resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.app.domain_name
    zone_id               = aws_cloudfront_distribution.app.hosted_zone_id
    evaluate_target_health = false
  }
}
