
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
  debug = var.debug

  providers = {
    docker = docker
  }
}
