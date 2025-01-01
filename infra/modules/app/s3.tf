resource "aws_s3_bucket" "private_bucket" {
  bucket = "${var.environment}-ustc-website-assets"
}
