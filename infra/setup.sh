#!/bin/bash

source ./helpers.sh

required_env_vars=(
  "AWS_SECRET_ACCESS_KEY"
  "AWS_ACCESS_KEY_ID"
  "ENVIRONMENT"
)
check_env_vars "${required_env_vars[@]}"

. ./init.sh
. ./load-secrets.sh

required_env_vars=(
  "DATABASE_PASSWORD"
  "SECRET_KEY"
  "DOMAIN_NAME"
  "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY"
  "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET"
  "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID"
)
check_env_vars "${required_env_vars[@]}"

export TF_VAR_database_password=$DATABASE_PASSWORD
export TF_VAR_bastion_public_key=$BASTION_PUBLIC_KEY
export TF_VAR_environment=$ENVIRONMENT
export TF_VAR_secret_key=$SECRET_KEY
export TF_VAR_domain_name=$DOMAIN_NAME
export TF_VAR_github_sha=$GITHUB_SHA
export TF_VAR_social_auth_azuread_tenant_oauth2_key=$SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY
export TF_VAR_social_auth_azuread_tenant_oauth2_secret=$SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET
export TF_VAR_social_auth_azuread_tenant_oauth2_tenant_id=$SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID
