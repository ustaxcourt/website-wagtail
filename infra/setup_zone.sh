#!/bin/bash

source ./helpers.sh

required_env_vars=(
  "DOMAIN_NAME"
)
check_env_vars "${required_env_vars[@]}"

if ! aws route53 list-hosted-zones-by-name --dns-name "${DOMAIN_NAME}" --max-items 1 | grep -q "\"Name\": \"${DOMAIN_NAME}.\""; then
  aws route53 create-hosted-zone --name "${DOMAIN_NAME}" --caller-reference $(date +%s)
else
  echo "Hosted zone for ${DOMAIN_NAME} already exists, skipping creation"
fi
