
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


variable "wagtailtransfer_secret_key" {
  type = string
  sensitive = true
}

variable "wagtailtransfer_sources" {
  type = string
  sensitive = true
}

variable "enable_error_test_pages" {
  description = "Exposes /alarm-test endpoints for manual alarm testing. Never enable in production."
  type        = string
  default     = "false"
}

variable "error_notification_emails" {
  description = "Recipients for human-readable website error notification emails. Normally supplied per-environment via the ERROR_NOTIFICATION_EMAILS secret (see infra/setup.sh); this default is the fallback when that's unset."
  type        = list(string)
  default     = []
}
