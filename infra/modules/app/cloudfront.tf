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

# Use AWS managed CachingOptimized policy for static content
data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

# Create custom cache policy for 5-minute caching
resource "aws_cloudfront_cache_policy" "custom_five_minute_app_cache" {
  name        = "${var.environment}-custom-five-minute-app-cache"
  comment     = "Policy for custom 5 minute application cache setting"
  min_ttl     = 0    # 0 minutes
  default_ttl = 300     # 5 minutes
  max_ttl     = 300     # 5 minutes

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
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
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}

# Create origin request policy for dynamic content
resource "aws_cloudfront_origin_request_policy" "dynamic_content" {
  name    = "${var.environment}-dynamic-content"
  comment = "Policy for dynamic content"

  cookies_config {
    cookie_behavior = "all"
  }

  headers_config {
    header_behavior = "allViewer"
  }

  query_strings_config {
    query_string_behavior = "all"
  }
}

# Create origin request policy for static content
resource "aws_cloudfront_origin_request_policy" "static_content" {
  name    = "${var.environment}-static-content"
  comment = "Policy for static content with necessary headers"

  cookies_config {
    cookie_behavior = "none"
  }
  headers_config {
    header_behavior = "whitelist"
    headers {
      items = ["Host", "Origin"]
    }
  }
  query_strings_config {
    query_string_behavior = "none"
  }
}

# Create cache policy for static content with 30 minute minimum TTL
resource "aws_cloudfront_cache_policy" "static_content" {
  name        = "${var.environment}-static-content"
  comment     = "Policy for static content with 30 minute minimum cache"
  min_ttl     = 1800    # 30 minutes
  default_ttl = 3600    # 1 hour
  max_ttl     = 86400   # 24 hours

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
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}

# Create VPC origin for CloudFront
resource "aws_cloudfront_vpc_origin" "app" {
  vpc_origin_endpoint_config {
    name                   = "${var.environment}-app-origin"
    arn                    = module.alb.lb_arn
    http_port              = 80
    https_port             = 443
    origin_protocol_policy = "https-only"

    origin_ssl_protocols {
      items    = ["TLSv1.2"]
      quantity = 1
    }
  }
}

resource "aws_cloudfront_origin_access_identity" "app" {
  comment = "Origin access identity for ${var.environment} app"
}

# Create S3 bucket for CloudFront logs
resource "aws_s3_bucket" "cloudfront_logs" {
  bucket        = var.environment == "sandbox" ? "${replace(var.domain_name, "-web.ustaxcourt.gov", "")}-ustc-website-cloudfront-logs": "${var.environment}-ustc-website-cloudfront-logs"
  force_destroy = true
}

resource "aws_s3_bucket_ownership_controls" "cloudfront_logs" {
  bucket = aws_s3_bucket.cloudfront_logs.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "cloudfront_logs" {
  depends_on = [aws_s3_bucket_ownership_controls.cloudfront_logs]
  bucket = aws_s3_bucket.cloudfront_logs.id
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "cloudfront_logs" {
  bucket = aws_s3_bucket.cloudfront_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Add bucket policy to allow CloudFront to write logs
resource "aws_s3_bucket_policy" "cloudfront_logs" {
  bucket = aws_s3_bucket.cloudfront_logs.id
  policy = data.aws_iam_policy_document.cloudfront_logs.json
}

data "aws_iam_policy_document" "cloudfront_logs" {
  statement {
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.cloudfront_logs.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.app.arn]
    }
  }
}

resource "aws_cloudfront_distribution" "app" {
  depends_on = [aws_s3_bucket_acl.cloudfront_logs]
  enabled = true
  is_ipv6_enabled = true
  price_class = "PriceClass_100"
  aliases = [var.domain_name, "www.${var.domain_name}"]

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.cloudfront_logs.bucket_domain_name
    prefix          = "cloudfront/"
  }

  origin {
    domain_name = module.alb.lb_dns_name
    origin_id   = "app-origin"

    vpc_origin_config {
      vpc_origin_id = aws_cloudfront_vpc_origin.app.id
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
    target_origin_id = "app-origin"

    cache_policy_id          = aws_cloudfront_cache_policy.custom_five_minute_app_cache.id
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

  # Cache behavior for /static/* path
  ordered_cache_behavior {
    path_pattern     = "/static/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "app-origin"

    cache_policy_id = aws_cloudfront_cache_policy.static_content.id
    origin_request_policy_id = aws_cloudfront_origin_request_policy.static_content.id

    viewer_protocol_policy = "redirect-to-https"
  }

  # Cache behavior for /admin path - no caching
  ordered_cache_behavior {
    path_pattern     = "/admin*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "app-origin"

    cache_policy_id          = data.aws_cloudfront_cache_policy.caching_disabled.id
    origin_request_policy_id = aws_cloudfront_origin_request_policy.dynamic_content.id

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
      values   = [aws_cloudfront_distribution.app.arn]
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
      values   = [aws_cloudfront_distribution.app.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "cloudfront_access_policy" {
  bucket = aws_s3_bucket.private_bucket.id
  policy = data.aws_iam_policy_document.s3_policy.json
}
