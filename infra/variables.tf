
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

variable "social_auth_azuread_tenant_oauth2_key" {
  type = string
}

variable "social_auth_azuread_tenant_oauth2_secret" {
  type = string
}

variable "social_auth_azuread_tenant_oauth2_tenant_id" {
  type = string
}

variable "prevent_db_deletion" {
  type = bool
  default = true
}
