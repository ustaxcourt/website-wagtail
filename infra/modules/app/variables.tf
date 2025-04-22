variable "database_password" {
  type = string
  sensitive = true
}

variable "bastion_public_key" {
  type = string
}

variable "environment" {
  type = string
}

variable "secret_key" {
  type = string
  sensitive = true
}

variable "domain_name" {
  description = "The domain name for the application (e.g., app.example.com)"
  type        = string
}

variable "github_sha" {
  description = "The GitHub SHA of the commit being deployed"
  type        = string
}

variable "cloudfront_origin_secret" {
  description = "Secret value for CloudFront origin header"
  type        = string
  sensitive   = true
}
