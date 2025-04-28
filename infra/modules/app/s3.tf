resource "aws_s3_bucket" "private_bucket" {
  bucket = var.environment == "sandbox" ? "${replace(var.domain_name, "-web.ustaxcourt.gov", "")}-ustc-website-assets": "${var.environment}-ustc-website-assets"
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket = aws_s3_bucket.private_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Add CORS configuration
resource "aws_s3_bucket_cors_configuration" "cors" {
  bucket = aws_s3_bucket.private_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*ustaxcourt.gov"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
