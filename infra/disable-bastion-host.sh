#!/bin/bash

AWS_DEFAULT_REGION="us-east-1"
export AWS_DEFAULT_REGION

source ./helpers.sh

required_env_vars=(
  "ENVIRONMENT"
)
check_env_vars "${required_env_vars[@]}"

# look up the bastion host by name "${var.environment}-bastion-host"
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=${ENVIRONMENT}-bastion-host" \
    --query "Reservations[*].Instances[*].InstanceId" \
    --output text)

if [ -z "$INSTANCE_ID" ]; then
    echo "No bastion host found with name ${ENVIRONMENT}-bastion-host"
    exit 1
fi

aws ec2 stop-instances --instance-ids $INSTANCE_ID
