#!/bin/bash

echo "WARNING: This will destroy the database and all data. Are you sure you want to continue? (Y/n)?"
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Aborting destruction process."
    exit 1
fi

source ./setup.sh

source ./delete-rds-instance.sh

terraform init \
    -upgrade \
    -backend=true \
    -backend-config=bucket="${STATE_BUCKET}" \
    -backend-config=key="${KEY}" \
    -backend-config=dynamodb_table="${LOCK_TABLE}" \
    -backend-config=region="${REGION}"
terraform plan -destroy -out destructive-plan
terraform apply destructive-plan
