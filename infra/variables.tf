
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
  type = string
}

variable "github_sha" {
  type = string
}

variable "cloudfront_origin_secret" {
  type = string
  sensitive = true
}
