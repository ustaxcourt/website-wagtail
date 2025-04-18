resource "aws_cloudfront_distribution" "files_distribution" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Files distribution for cody-sandbox-files.ustaxcourt.gov"
  default_root_object = "index.html"
  price_class         = "PriceClass_100"  # US, Canada, Europe

  aliases = ["cody-sandbox-files.ustaxcourt.gov"]

  origin {
    domain_name = aws_s3_bucket.private_bucket.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.private_bucket.id}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.files_oai.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
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
