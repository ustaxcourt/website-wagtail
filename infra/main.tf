
data "aws_caller_identity" "this" {}
data "aws_ecr_authorization_token" "this" {}
data "aws_region" "this" {}

module "app" {
  source = "./modules/app"
  bastion_public_key = var.bastion_public_key
  database_password = var.database_password
  environment = var.environment
  providers = {
    docker = docker
  }
}