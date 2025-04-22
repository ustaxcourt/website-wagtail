resource "aws_cloudfront_function" "rewrite_uri" {
  name    = "${var.environment}-rewrite-uri"
  runtime = "cloudfront-js-1.0"
  comment = "Function to strip /files prefix from request URI"
  publish = true
  code    = <<-EOT
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // Check if the URI starts with /files/ and remove it
    if (uri.startsWith('/files/')) {
        request.uri = uri.slice(6); // Remove '/files'
    }

    return request;
}
EOT
}

# Use AWS managed CachingDisabled policy for dynamic content
data "aws_cloudfront_cache_policy" "caching_disabled" {
  name = "Managed-CachingDisabled"
}

# Create origin request policy for dynamic content
resource "aws_cloudfront_origin_request_policy" "dynamic_content" {
  name    = "${var.environment}-dynamic-content"
  comment = "Policy for dynamic content"

  cookies_config {
    cookie_behavior = "all"
  }
  headers_config {
    header_behavior = "whitelist"
    headers {
      items = ["Host", "Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]
    }
  }
  query_strings_config {
    query_string_behavior = "all"
  }
}

# Create cache policy for static content
resource "aws_cloudfront_cache_policy" "static_content" {
  name        = "${var.environment}-static-content"
  comment     = "Policy for static content with standard caching"
  min_ttl     = 0
  default_ttl = 3600
  max_ttl     = 86400

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "none"
    }
  }
}

resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Main distribution for ${var.domain_name}"
  price_class         = "PriceClass_100"  # US, Canada, Europe

  aliases = [var.domain_name]

  # ALB Origin
  origin {
    domain_name = module.alb.lb_dns_name
    origin_id   = "ALB-${module.alb.lb_id}"

    custom_origin_config {
      http_port              = 80
      https_port            = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols  = ["TLSv1.2"]
    }
  }

  # S3 Origin
  origin {
    domain_name              = aws_s3_bucket.private_bucket.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.private_bucket.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.default.id
  }

  # Default cache behavior (for ALB)
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${module.alb.lb_id}"

    cache_policy_id          = data.aws_cloudfront_cache_policy.caching_disabled.id
    origin_request_policy_id = aws_cloudfront_origin_request_policy.dynamic_content.id

    viewer_protocol_policy = "redirect-to-https"
  }

  # Cache behavior for /files/* path
  ordered_cache_behavior {
    path_pattern     = "/files/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.private_bucket.id}"

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.rewrite_uri.arn
    }

    cache_policy_id = aws_cloudfront_cache_policy.static_content.id

    viewer_protocol_policy = "redirect-to-https"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.main.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}

# Create Origin Access Control
resource "aws_cloudfront_origin_access_control" "default" {
  name                              = "S3 OAC ${var.environment}"
  description                       = "Origin Access Control for S3"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# S3 bucket policy to allow CloudFront access using OAC
data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.private_bucket.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.main.arn]
    }
  }

  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.private_bucket.arn]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.main.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "cloudfront_access_policy" {
  bucket = aws_s3_bucket.private_bucket.id
  policy = data.aws_iam_policy_document.s3_policy.json
}
