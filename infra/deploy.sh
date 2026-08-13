#!/bin/bash

set -euo pipefail

source ./setup.sh

source ./setup_zone.sh

./update-deployer-policy.sh

terraform_init() {
    terraform init \
        -upgrade \
        -backend=true \
        -backend-config=bucket="${STATE_BUCKET}" \
        -backend-config=key="${KEY}" \
        -backend-config=dynamodb_table="${LOCK_TABLE}" \
        -backend-config=region="${REGION}"
}

max_attempts=3
attempt=1
until terraform_init; do
    if [ "${attempt}" -ge "${max_attempts}" ]; then
        echo "terraform init failed after ${max_attempts} attempts" >&2
        exit 1
    fi

    echo "terraform init failed on attempt ${attempt}; retrying..." >&2
    attempt=$((attempt + 1))
done

terraform plan -out execution-plan
terraform apply execution-plan
