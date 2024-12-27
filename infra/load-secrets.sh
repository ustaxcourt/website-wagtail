#!/bin/bash -e

content=$(aws secretsmanager get-secret-value --region us-east-1 --secret-id "website_secrets" --query "SecretString" --output text)
echo "${content}" | jq -r 'to_entries|map("\(.key)=\"\(.value)\"")|.[]' > .env
set -o allexport
source .env
set +o allexport
