
data "aws_caller_identity" "this" {}
data "aws_ecr_authorization_token" "this" {}
data "aws_region" "this" {}

module "app" {
  source = "./modules/app"
  bastion_public_key = var.bastion_public_key
  database_password = var.database_password
  secret_key = var.secret_key
  environment = var.environment
  domain_name = var.domain_name
  github_sha = var.github_sha
  social_auth_azuread_tenant_oauth2_key = var.social_auth_azuread_tenant_oauth2_key
  social_auth_azuread_tenant_oauth2_secret = var.social_auth_azuread_tenant_oauth2_secret
  social_auth_azuread_tenant_oauth2_tenant_id = var.social_auth_azuread_tenant_oauth2_tenant_id
  prevent_db_deletion = var.prevent_db_deletion
  providers = {
    docker = docker
  }
}
