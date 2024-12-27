#!/bin/bash

# Verify script is run from infra directory
if [[ $(basename "$PWD") != "infra" ]]; then
    echo "Error: This script must be run from the infra directory"
    exit 1
fi


# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/deployer-policy"
POLICY_FILE="./iam/deployer-policy.json"

# Check if policy file exists
if [ ! -f "$POLICY_FILE" ]; then
    echo "Error: Policy file not found at $POLICY_FILE"
    exit 1
fi

# Create new policy version and set as default
aws iam create-policy-version \
    --policy-arn "$POLICY_ARN" \
    --policy-document "file://$POLICY_FILE" \
    --set-as-default

if [ $? -eq 0 ]; then
    echo "Successfully updated policy $POLICY_ARN"
else
    echo "Failed to update policy"
    exit 1
fi
