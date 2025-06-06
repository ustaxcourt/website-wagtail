#!/bin/bash

source ./setup.sh

source ./setup_zone.sh

./update-deployer-policy.sh

terraform init \
    -upgrade \
    -backend=true \
    -backend-config=bucket="${STATE_BUCKET}" \
    -backend-config=key="${KEY}" \
    -backend-config=dynamodb_table="${LOCK_TABLE}" \
    -backend-config=region="${REGION}"
terraform plan -out execution-plan
terraform apply execution-plan
