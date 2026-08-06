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

variable "prevent_db_deletion" {
  description = "Whether to prevent the database from being deleted"
  type        = bool
}

variable "social_auth_azuread_tenant_oauth2_key" {
  description = "The Azure AD tenant OAuth2 key"
  type = string
}

variable "social_auth_azuread_tenant_oauth2_secret" {
  description = "The Azure AD tenant OAuth2 secret"
  type = string
}

variable "social_auth_azuread_tenant_oauth2_tenant_id" {
  description = "The Azure AD tenant ID"
  type = string
}

variable "email_scheduler_enabled_environments" {
  description = "A list of environments where the email moderator digest scheduler should be enabled."
  type        = list(string)
  default     = ["production", "train"]
}

variable "wagtailtransfer_secret_key" {
  type = string
  sensitive = true
}

variable "wagtailtransfer_sources" {
  type = string
  sensitive = true
}

variable "error_notification_emails" {
  description = "Recipients for human-readable website error notification emails."
  type        = list(string)
}
