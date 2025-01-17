resource "aws_s3_bucket" "private_bucket" {
  bucket = "${var.domain_name}-ustc-website-assets"
}

# Add a bucket policy for public access
resource "aws_s3_bucket_policy" "public_access_policy" {
  bucket = aws_s3_bucket.private_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "s3:GetObject"
        Resource = "${aws_s3_bucket.private_bucket.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.public_access]
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket = aws_s3_bucket.private_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Add CORS configuration
resource "aws_s3_bucket_cors_configuration" "cors" {
  bucket = aws_s3_bucket.private_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*ustaxcourt.gov"] # Adjust based on your needs
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
