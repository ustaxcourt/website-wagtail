
data "aws_caller_identity" "this" {}
data "aws_ecr_authorization_token" "this" {}
data "aws_region" "this" {}

locals {
  container_name = "website-container"
  container_port = 8000
  ecr_address    = format("%v.dkr.ecr.%v.amazonaws.com", data.aws_caller_identity.this.account_id, data.aws_region.this.name)
}
