#!/bin/bash

# this is a util script which will disable delete protection for the RDS instance
# and then delete the instance.

export AWS_PAGER=""

# Find the first RDS instance with environment prefix
instance_id=$(aws rds describe-db-instances \
    --query "DBInstances[?starts_with(DBInstanceIdentifier, '${ENVIRONMENT}')].DBInstanceIdentifier" \
    --output text \
    --region us-east-1 \
    | cut -f1)

if [ -z "$instance_id" ]; then
    echo "No RDS instance found with prefix ${ENVIRONMENT}, continuing to run terraform destroy"
else
    echo "Found RDS instance: ${instance_id}"

    aws rds modify-db-instance \
        --db-instance-identifier "${instance_id}" \
        --no-deletion-protection \
        --region us-east-1

    aws rds delete-db-instance \
        --db-instance-identifier "${instance_id}" \
        --skip-final-snapshot \
        --region us-east-1
fi
