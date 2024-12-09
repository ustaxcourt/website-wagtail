#!/bin/bash

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)

if [ -z "$AWS_ACCOUNT_ID" ]; then
  echo "Error: Unable to retrieve AWS account ID. Please check your AWS CLI configuration."
  exit 1
fi

KEY="terraform.tfstate"
REGION='us-east-1'
STATE_BUCKET="${AWS_ACCOUNT_ID}-website-taxcourt-terraform-state"
LOCK_TABLE="terraform-locks"
