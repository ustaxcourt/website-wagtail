#!/bin/bash

source ./helpers.sh
required_env_vars=(
  "AWS_SECRET_ACCESS_KEY"
  "AWS_ACCESS_KEY_ID"
)
check_env_vars "${required_env_vars[@]}"

. ./init.sh
. ./load-secrets.sh

required_env_vars=(
  "DATABASE_PASSWORD"
)
check_env_vars "${required_env_vars[@]}"

export TF_VAR_database_password=$DATABASE_PASSWORD

terraform init \
    -upgrade \
    -backend=true \
    -backend-config=bucket="${STATE_BUCKET}" \
    -backend-config=key="${KEY}" \
    -backend-config=dynamodb_table="${LOCK_TABLE}" \
    -backend-config=region="${REGION}"
terraform plan -out execution-plan
terraform apply --auto-approve execution-plan
