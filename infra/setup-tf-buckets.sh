#!/bin/bash -e

# aws configure set cli_pager ""

# Lookup the current AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)

if [ -z "$AWS_ACCOUNT_ID" ]; then
  echo "Error: Unable to retrieve AWS account ID. Please check your AWS CLI configuration."
  exit 1
fi

STATE_BUCKET="${AWS_ACCOUNT_ID}-website-taxcourt-terraform-state"

# create a unique bucket which will store the tf state
aws s3api create-bucket --bucket $STATE_BUCKET --region us-east-1
aws s3api put-bucket-versioning --bucket $STATE_BUCKET --versioning-configuration Status=Enabled

# create the dynamodb table used for the locking
LOCK_TABLE="terraform-locks"
echo "Checking if DynamoDB table $LOCK_TABLE exists..."

set +e
aws dynamodb describe-table --region us-east-1 --table-name $LOCK_TABLE --query "Table.TableStatus" --output text --no-cli-pager
code=$?
set -e

if [ "${code}" == 0 ]; then
  echo "DynamoDB table $LOCK_TABLE already exists. Skipping creation."
else
  echo "Creating DynamoDB table: $LOCK_TABLE"
  aws dynamodb create-table \
      --region us-east-1 \
      --table-name $LOCK_TABLE \
      --attribute-definitions AttributeName=LockID,AttributeType=S \
      --key-schema AttributeName=LockID,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST \
      --no-cli-pager

  echo "Waiting for DynamoDB table to become active..."
  aws dynamodb wait table-exists --table-name $LOCK_TABLE --region us-east-1
fi

echo "Setup complete for AWS account: $AWS_ACCOUNT_ID"
