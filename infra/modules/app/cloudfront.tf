resource "aws_cloudfront_function" "rewrite_uri" {
  name    = "${var.environment}-rewrite-uri"
  runtime = "cloudfront-js-1.0"
  comment = "Function to redirect legacy URIs and strip /files prefix from other requests"
  publish = true
  code    = <<-EOT
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    if (uri.startsWith('/files/')) {
      // --- Redirect Map ---
      var redirects = {
          "/files/documents/Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf": "/files/documents/complete-ropp.pdf",
          "/files/documents/Rule-100.pdf": "/files/documents/rule-100.pdf",
          "/files/documents/Rule-101.pdf": "/files/documents/rule-101.pdf",
          "/files/documents/Rule-102.pdf": "/files/documents/rule-102.pdf",
          "/files/documents/Rule-103_Amended_03202023.pdf": "/files/documents/rule-103.pdf",
          "/files/documents/Rule-104.pdf": "/files/documents/rule-104.pdf",
          "/files/documents/Rule-10_Amended_03202023.pdf": "/files/documents/rule-10.pdf",
          "/files/documents/Rule-110_Amended_03202023.pdf": "/files/documents/rule-110.pdf",
          "/files/documents/Rule-11superseded.pdf": "/files/documents/rule-11.pdf",
          "/files/documents/Rule-120.pdf": "/files/documents/rule-120.pdf",
          "/files/documents/Rule-121.pdf": "/files/documents/rule-121.pdf",
          "/files/documents/Rule-121_Amended_03202023.pdf": "/files/documents/rule-121.pdf",
          "/files/documents/Rule-122.pdf": "/files/documents/rule-122.pdf",
          "/files/documents/Rule-123.pdf": "/files/documents/rule-123.pdf",
          "/files/documents/Rule-124.pdf": "/files/documents/rule-124.pdf",
          "/files/documents/Rule-12superseded.pdf": "/files/documents/rule-12.pdf",
          "/files/documents/Rule-130.pdf": "/files/documents/rule-130.pdf",
          "/files/documents/Rule-131.pdf": "/files/documents/rule-131.pdf",
          "/files/documents/Rule-132.pdf": "/files/documents/rule-132.pdf",
          "/files/documents/Rule-133_Amended_03202023.pdf": "/files/documents/rule-133.pdf",
          "/files/documents/Rule-13_amended_08082024.pdf": "/files/documents/rule-13.pdf",
          "/files/documents/Rule-140_Amended_03202023.pdf": "/files/documents/rule-140.pdf",
          "/files/documents/Rule-141_Amended_03202023.pdf": "/files/documents/rule-141.pdf",
          "/files/documents/Rule-142.pdf": "/files/documents/rule-142.pdf",
          "/files/documents/Rule-143amended.pdf": "/files/documents/rule-143.pdf",
          "/files/documents/Rule-144.pdf": "/files/documents/rule-144.pdf",
          "/files/documents/Rule-145.pdf": "/files/documents/rule-145.pdf",
          "/files/documents/Rule-146.pdf": "/files/documents/rule-146.pdf",
          "/files/documents/Rule-147.pdf": "/files/documents/rule-147.pdf",
          "/files/documents/Rule-147_Amended_03202023.pdf": "/files/documents/rule-147.pdf",
          "/files/documents/Rule-148.pdf": "/files/documents/rule-148.pdf",
          "/files/documents/Rule-149.pdf": "/files/documents/rule-149.pdf",
          "/files/documents/Rule-150.pdf": "/files/documents/rule-150.pdf",
          "/files/documents/Rule-151.pdf": "/files/documents/rule-151.pdf",
          "/files/documents/Rule-151_1_Amended_03202023.pdf": "/files/documents/rule-151.1.pdf",
          "/files/documents/Rule-151_Amended_03202023.pdf": "/files/documents/rule-151.pdf",
          "/files/documents/Rule-152_Amended_03202023.pdf": "/files/documents/rule-152.pdf",
          "/files/documents/Rule-155.pdf": "/files/documents/rule-155.pdf",
          "/files/documents/Rule-156.pdf": "/files/documents/rule-156.pdf",
          "/files/documents/Rule-157.pdf": "/files/documents/rule-157.pdf",
          "/files/documents/Rule-160.pdf": "/files/documents/rule-160.pdf",
          "/files/documents/Rule-161_Amended_03202023.pdf": "/files/documents/rule-161.pdf",
          "/files/documents/Rule-162.pdf": "/files/documents/rule-162.pdf",
          "/files/documents/Rule-163.pdf": "/files/documents/rule-163.pdf",
          "/files/documents/Rule-170_Amended_03202023.pdf": "/files/documents/rule-170.pdf",
          "/files/documents/Rule-171_Amended_03202023.pdf": "/files/documents/rule-171.pdf",
          "/files/documents/Rule-172.pdf": "/files/documents/rule-172.pdf",
          "/files/documents/Rule-173.pdf": "/files/documents/rule-173.pdf",
          "/files/documents/Rule-174.pdf": "/files/documents/rule-174.pdf",
          "/files/documents/Rule-180_Amended_03202023.pdf": "/files/documents/rule-180.pdf",
          "/files/documents/Rule-181.pdf": "/files/documents/rule-181.pdf",
          "/files/documents/Rule-182_Amended_03202023.pdf": "/files/documents/rule-182.pdf",
          "/files/documents/Rule-183.pdf": "/files/documents/rule-183.pdf",
          "/files/documents/Rule-190.pdf": "/files/documents/rule-190.pdf",
          "/files/documents/Rule-191.pdf": "/files/documents/rule-191.pdf",
          "/files/documents/Rule-192.pdf": "/files/documents/rule-192.pdf",
          "/files/documents/Rule-193.pdf": "/files/documents/rule-193.pdf",
          "/files/documents/Rule-1_Amended_03202023.pdf": "/files/documents/rule-1.pdf",
          "/files/documents/Rule-2.pdf": "/files/documents/rule-2.pdf",
          "/files/documents/Rule-2002nd-amended.pdf": "/files/documents/rule-2002.pdf",
          "/files/documents/Rule-201.pdf": "/files/documents/rule-201.pdf",
          "/files/documents/Rule-202.pdf": "/files/documents/rule-202.pdf",
          "/files/documents/Rule-20_Amended_03202023.pdf": "/files/documents/rule-20.pdf",
          "/files/documents/Rule-21.pdf": "/files/documents/rule-21.pdf",
          "/files/documents/Rule-210_amended_08082024.pdf": "/files/documents/rule-210.pdf",
          "/files/documents/Rule-211.pdf": "/files/documents/rule-211.pdf",
          "/files/documents/Rule-212.pdf": "/files/documents/rule-212.pdf",
          "/files/documents/Rule-213_Amended_03202023.pdf": "/files/documents/rule-213.pdf",
          "/files/documents/Rule-214.pdf": "/files/documents/rule-214.pdf",
          "/files/documents/Rule-215.pdf": "/files/documents/rule-215.pdf",
          "/files/documents/Rule-216.pdf": "/files/documents/rule-216.pdf",
          "/files/documents/Rule-217_Amended_03202023.pdf": "/files/documents/rule-217.pdf",
          "/files/documents/Rule-218.pdf": "/files/documents/rule-218.pdf",
          "/files/documents/Rule-21_Amended_03202023.pdf": "/files/documents/rule-21.pdf",
          "/files/documents/Rule-220_amended_08082024.pdf": "/files/documents/rule-220.pdf",
          "/files/documents/Rule-221.pdf": "/files/documents/rule-221.pdf",
          "/files/documents/Rule-222.pdf": "/files/documents/rule-222.pdf",
          "/files/documents/Rule-223.pdf": "/files/documents/rule-223.pdf",
          "/files/documents/Rule-224.pdf": "/files/documents/rule-224.pdf",
          "/files/documents/Rule-225.pdf": "/files/documents/rule-225.pdf",
          "/files/documents/Rule-226.pdf": "/files/documents/rule-226.pdf",
          "/files/documents/Rule-227.pdf": "/files/documents/rule-227.pdf",
          "/files/documents/Rule-228.pdf": "/files/documents/rule-228.pdf",
          "/files/documents/Rule-229.pdf": "/files/documents/rule-229.pdf",
          "/files/documents/Rule-229A.pdf": "/files/documents/rule-229A.pdf",
          "/files/documents/Rule-22amended.pdf": "/files/documents/rule-22.pdf",
          "/files/documents/Rule-2302nd-amended.pdf": "/files/documents/rule-2302.pdf",
          "/files/documents/Rule-231_Amended_03202023.pdf": "/files/documents/rule-231.pdf",
          "/files/documents/Rule-232.pdf": "/files/documents/rule-232.pdf",
          "/files/documents/Rule-233_Amended_03202023.pdf": "/files/documents/rule-233.pdf",
          "/files/documents/Rule-23_Amended_03202023.pdf": "/files/documents/rule-23.pdf",
          "/files/documents/Rule-240_amended_08082024.pdf": "/files/documents/rule-240.pdf",
          "/files/documents/Rule-241.pdf": "/files/documents/rule-241.pdf",
          "/files/documents/Rule-242.pdf": "/files/documents/rule-242.pdf",
          "/files/documents/Rule-243.pdf": "/files/documents/rule-243.pdf",
          "/files/documents/Rule-244.pdf": "/files/documents/rule-244.pdf",
          "/files/documents/Rule-245.pdf": "/files/documents/rule-245.pdf",
          "/files/documents/Rule-246.pdf": "/files/documents/rule-246.pdf",
          "/files/documents/Rule-247.pdf": "/files/documents/rule-247.pdf",
          "/files/documents/Rule-248.pdf": "/files/documents/rule-248.pdf",
          "/files/documents/Rule-249.pdf": "/files/documents/rule-249.pdf",
          "/files/documents/Rule-24amended-Oct.-6-2020.pdf": "/files/documents/rule-24.pdf",
          "/files/documents/Rule-250.pdf": "/files/documents/rule-250.pdf",
          "/files/documents/Rule-251.pdf": "/files/documents/rule-251.pdf",
          "/files/documents/Rule-255.1_amended_08082024.pdf": "/files/documents/rule-255.1.pdf",
          "/files/documents/Rule-255.2New.pdf": "/files/documents/rule-255.2.pdf",
          "/files/documents/Rule-255.3New.pdf": "/files/documents/rule-255.3.pdf",
          "/files/documents/Rule-255.4New.pdf": "/files/documents/rule-255.4.pdf",
          "/files/documents/Rule-255.5New.pdf": "/files/documents/rule-255.5.pdf",
          "/files/documents/Rule-255.6New.pdf": "/files/documents/rule-255.6.pdf",
          "/files/documents/Rule-255.7New.pdf": "/files/documents/rule-255.7.pdf",
          "/files/documents/Rule-25_Amended_03202023.pdf": "/files/documents/rule-25.pdf",
          "/files/documents/Rule-260amended-Oct.-6-2020.pdf": "/files/documents/rule-260.pdf",
          "/files/documents/Rule-261amended-Oct.-6-2020.pdf": "/files/documents/rule-261.pdf",
          "/files/documents/Rule-262amended-Oct.-6-2020.pdf": "/files/documents/rule-262.pdf",
          "/files/documents/Rule-26_Amended_03202023.pdf": "/files/documents/rule-26.pdf",
          "/files/documents/Rule-27.pdf": "/files/documents/rule-27.pdf",
          "/files/documents/Rule-270_amended_08082024.pdf": "/files/documents/rule-270.pdf",
          "/files/documents/Rule-271.pdf": "/files/documents/rule-271.pdf",
          "/files/documents/Rule-272.pdf": "/files/documents/rule-272.pdf",
          "/files/documents/Rule-273.pdf": "/files/documents/rule-273.pdf",
          "/files/documents/Rule-274.pdf": "/files/documents/rule-274.pdf",
          "/files/documents/Rule-27_Amended_03202023.pdf": "/files/documents/rule-27.pdf",
          "/files/documents/Rule-280_amended_08082024.pdf": "/files/documents/rule-280.pdf",
          "/files/documents/Rule-280amended.pdf": "/files/documents/rule-280.pdf",
          "/files/documents/Rule-281amended.pdf": "/files/documents/rule-281.pdf",
          "/files/documents/Rule-282.pdf": "/files/documents/rule-282.pdf",
          "/files/documents/Rule-283.pdf": "/files/documents/rule-283.pdf",
          "/files/documents/Rule-284.pdf": "/files/documents/rule-284.pdf",
          "/files/documents/Rule-290_amended_08082024.pdf": "/files/documents/rule-290.pdf",
          "/files/documents/Rule-291.pdf": "/files/documents/rule-291.pdf",
          "/files/documents/Rule-292.pdf": "/files/documents/rule-292.pdf",
          "/files/documents/Rule-293.pdf": "/files/documents/rule-293.pdf",
          "/files/documents/Rule-294.pdf": "/files/documents/rule-294.pdf",
          "/files/documents/Rule-30.pdf": "/files/documents/rule-30.pdf",
          "/files/documents/Rule-300_amended_08082024.pdf": "/files/documents/rule-300.pdf",
          "/files/documents/Rule-301.pdf": "/files/documents/rule-301.pdf",
          "/files/documents/Rule-302.pdf": "/files/documents/rule-302.pdf",
          "/files/documents/Rule-303.pdf": "/files/documents/rule-303.pdf",
          "/files/documents/Rule-304.pdf": "/files/documents/rule-304.pdf",
          "/files/documents/Rule-305.pdf": "/files/documents/rule-305.pdf",
          "/files/documents/Rule-310_amended_08082024.pdf": "/files/documents/rule-310.pdf",
          "/files/documents/Rule-311.pdf": "/files/documents/rule-311.pdf",
          "/files/documents/Rule-312.pdf": "/files/documents/rule-312.pdf",
          "/files/documents/Rule-313.pdf": "/files/documents/rule-313.pdf",
          "/files/documents/Rule-314.pdf": "/files/documents/rule-314.pdf",
          "/files/documents/Rule-315.pdf": "/files/documents/rule-315.pdf",
          "/files/documents/Rule-316.pdf": "/files/documents/rule-316.pdf",
          "/files/documents/Rule-31_Amended_03202023.pdf": "/files/documents/rule-31.pdf",
          "/files/documents/Rule-320.pdf": "/files/documents/rule-320.pdf",
          "/files/documents/Rule-321.pdf": "/files/documents/rule-321.pdf",
          "/files/documents/Rule-322.pdf": "/files/documents/rule-322.pdf",
          "/files/documents/Rule-323.pdf": "/files/documents/rule-323.pdf",
          "/files/documents/Rule-324.pdf": "/files/documents/rule-324.pdf",
          "/files/documents/Rule-325.pdf": "/files/documents/rule-325.pdf",
          "/files/documents/Rule-32_Amended_03202023.pdf": "/files/documents/rule-32.pdf",
          "/files/documents/Rule-330.pdf": "/files/documents/rule-330.pdf",
          "/files/documents/Rule-331.pdf": "/files/documents/rule-331.pdf",
          "/files/documents/Rule-332.pdf": "/files/documents/rule-332.pdf",
          "/files/documents/Rule-333.pdf": "/files/documents/rule-333.pdf",
          "/files/documents/Rule-334.pdf": "/files/documents/rule-334.pdf",
          "/files/documents/Rule-33_Amended_03202023.pdf": "/files/documents/rule-33.pdf",
          "/files/documents/Rule-340.pdf": "/files/documents/rule-340.pdf",
          "/files/documents/Rule-341.pdf": "/files/documents/rule-341.pdf",
          "/files/documents/Rule-342.pdf": "/files/documents/rule-342.pdf",
          "/files/documents/Rule-343.pdf": "/files/documents/rule-343.pdf",
          "/files/documents/Rule-344.pdf": "/files/documents/rule-344.pdf",
          "/files/documents/Rule-345.pdf": "/files/documents/rule-345.pdf",
          "/files/documents/Rule-34_Amended_03202023.pdf": "/files/documents/rule-34.pdf",
          "/files/documents/Rule-350.pdf": "/files/documents/rule-350.pdf",
          "/files/documents/Rule-351.pdf": "/files/documents/rule-351.pdf",
          "/files/documents/Rule-352.pdf": "/files/documents/rule-352.pdf",
          "/files/documents/Rule-353.pdf": "/files/documents/rule-353.pdf",
          "/files/documents/Rule-354.pdf": "/files/documents/rule-354.pdf",
          "/files/documents/Rule-35_Amended_03202023.pdf": "/files/documents/rule-35.pdf",
          "/files/documents/Rule-36_Amended_03202023.pdf": "/files/documents/rule-36.pdf",
          "/files/documents/Rule-37.pdf": "/files/documents/rule-37.pdf",
          "/files/documents/Rule-38amended.pdf": "/files/documents/rule-38.pdf",
          "/files/documents/Rule-39.pdf": "/files/documents/rule-39.pdf",
          "/files/documents/Rule-3_Amended_03202023.pdf": "/files/documents/rule-3.pdf",
          "/files/documents/Rule-40.pdf": "/files/documents/rule-40.pdf",
          "/files/documents/Rule-41_amended_08082024.pdf": "/files/documents/rule-41.pdf",
          "/files/documents/Rule-50.pdf": "/files/documents/rule-50.pdf",
          "/files/documents/Rule-51.pdf": "/files/documents/rule-51.pdf",
          "/files/documents/Rule-52.pdf": "/files/documents/rule-52.pdf",
          "/files/documents/Rule-53.pdf": "/files/documents/rule-53.pdf",
          "/files/documents/Rule-54.pdf": "/files/documents/rule-54.pdf",
          "/files/documents/Rule-55.pdf": "/files/documents/rule-55.pdf",
          "/files/documents/Rule-56.pdf": "/files/documents/rule-56.pdf",
          "/files/documents/Rule-57..pdf": "/files/documents/rule-57.pdf",
          "/files/documents/Rule-58.pdf": "/files/documents/rule-58.pdf",
          "/files/documents/Rule-60amended.pdf": "/files/documents/rule-60.pdf",
          "/files/documents/Rule-61_Amended_03202023.pdf": "/files/documents/rule-61.pdf",
          "/files/documents/Rule-62_Amended_03202023.pdf": "/files/documents/rule-62.pdf",
          "/files/documents/Rule-63_Amended_03202023.pdf": "/files/documents/rule-63.pdf",
          "/files/documents/Rule-64_Amended_03202023.pdf": "/files/documents/rule-64.pdf",
          "/files/documents/Rule-70_Amended_03202023.pdf": "/files/documents/rule-70.pdf",
          "/files/documents/Rule-71.pdf": "/files/documents/rule-71.pdf",
          "/files/documents/Rule-72.pdf": "/files/documents/rule-72.pdf",
          "/files/documents/Rule-73.pdf": "/files/documents/rule-73.pdf",
          "/files/documents/Rule-74_Amended_03202023.pdf": "/files/documents/rule-74.pdf",
          "/files/documents/Rule-74amended.pdf": "/files/documents/rule-74.pdf",
          "/files/documents/Rule-80.pdf": "/files/documents/rule-80.pdf",
          "/files/documents/Rule-81.pdf": "/files/documents/rule-81.pdf",
          "/files/documents/Rule-81_Amended_03202023.pdf": "/files/documents/rule-81.pdf",
          "/files/documents/Rule-82.pdf": "/files/documents/rule-82.pdf",
          "/files/documents/Rule-83.pdf": "/files/documents/rule-83.pdf",
          "/files/documents/Rule-84.pdf": "/files/documents/rule-84.pdf",
          "/files/documents/Rule-85.pdf": "/files/documents/rule-85.pdf",
          "/files/documents/Rule-90_Amended_03202023.pdf": "/files/documents/rule-90.pdf",
          "/files/documents/Rule-91_Amended_03202023.pdf": "/files/documents/rule-91.pdf",
          "/files/documents/Rule-92_Amended_03202023.pdf": "/files/documents/rule-92.pdf",
          "/files/documents/Rule-93_Amended_03202023.pdf": "/files/documents/rule-93.pdf"
      };

      // If the requested URI is in our redirect map, return a 302 response.
          if (redirects.hasOwnProperty(uri)) {
        return {
            statusCode: 302,
            statusDescription: "Found",
            headers: {
                location: { value: redirects[uri] }
            }
        };
    }

    // --- URI Rewrite ---
    if (uri.startsWith('/files/')) {
        request.uri = uri.slice(6); // Removes '/files' prefix
    }

    // Return the modified request to continue to the origin.
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
