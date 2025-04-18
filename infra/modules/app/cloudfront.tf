resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Main distribution for ${var.domain_name}"
  default_root_object = "index.html"
  price_class         = "PriceClass_100"  # US, Canada, Europe

  aliases = [var.domain_name]

  # ALB Origin
  origin {
    domain_name = module.alb.lb_dns_name
    origin_id   = "ALB-${module.alb.lb_id}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"  # Only use HTTPS to origin
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # S3 Origin
  origin {
    domain_name = aws_s3_bucket.private_bucket.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.private_bucket.id}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.files_oai.cloudfront_access_identity_path
    }
  }

  # Default cache behavior (for ALB)
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${module.alb.lb_id}"

    forwarded_values {
      query_string = true
      headers      = ["Host", "Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]
      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"  # Redirect HTTP to HTTPS
    min_ttl                = 0
    default_ttl           = 0  # Don't cache dynamic content by default
    max_ttl              = 0
  }

  # Cache behavior for /files/* path
  ordered_cache_behavior {
    path_pattern     = "/files/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.private_bucket.id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl           = 3600
    max_ttl              = 86400
  }

  # Cache behavior for static files
  ordered_cache_behavior {
    path_pattern     = "/static/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${module.alb.lb_id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl           = 86400  # Cache static files for 24 hours
    max_ttl              = 31536000  # Maximum cache time of 1 year
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

resource "aws_cloudfront_origin_access_identity" "files_oai" {
  comment = "OAI for files distribution"
}

# Update S3 bucket policy to allow CloudFront access
resource "aws_s3_bucket_policy" "files_bucket_policy" {
  bucket = aws_s3_bucket.private_bucket.id
  policy = data.aws_iam_policy_document.s3_policy.json
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.private_bucket.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.files_oai.iam_arn]
    }
  }
}
