#!/bin/bash

# Set your variables
ENVIRONMENT="sandbox"
NEW_INSTANCE_NAME="${ENVIRONMENT}-restored-instance"
SNAPSHOT_ID="rds:sandbox-20250414132738462100000007-2025-04-14-13-31"
NEW_PASSWORD="your-new-password"

# Get the existing RDS instance info and save key parameters
INSTANCE_INFO=$(aws rds describe-db-instances --output json)

# Extract the necessary values using jq
VPC_SECURITY_GROUP_ID=$(echo $INSTANCE_INFO | jq -r '.DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId')
DB_SUBNET_GROUP=$(echo $INSTANCE_INFO | jq -r '.DBInstances[0].DBSubnetGroup.DBSubnetGroupName')
AVAILABILITY_ZONE=$(echo $INSTANCE_INFO | jq -r '.DBInstances[0].AvailabilityZone')
STORAGE_TYPE=$(echo $INSTANCE_INFO | jq -r '.DBInstances[0].StorageType')
DB_INSTANCE_CLASS=$(echo $INSTANCE_INFO | jq -r '.DBInstances[0].DBInstanceClass')

# Print what we're about to do
echo "Creating restored instance '${NEW_INSTANCE_NAME}' from snapshot '${SNAPSHOT_ID}'"
echo "Using security group: ${VPC_SECURITY_GROUP_ID}"
echo "Using subnet group: ${DB_SUBNET_GROUP}"
echo "Using availability zone: ${AVAILABILITY_ZONE}"

# Restore the RDS instance from the snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier "${NEW_INSTANCE_NAME}" \
  --db-snapshot-identifier "${SNAPSHOT_ID}" \
  --db-instance-class "${DB_INSTANCE_CLASS}" \
  --vpc-security-group-ids "${VPC_SECURITY_GROUP_ID}" \
  --db-subnet-group-name "${DB_SUBNET_GROUP}" \
  --availability-zone "${AVAILABILITY_ZONE}" \
  --no-publicly-accessible \
  --storage-type "${STORAGE_TYPE}" \
  --deletion-protection

echo "Restore command submitted. Waiting for instance to become available..."

# Wait for the instance to become available
while true; do
  STATUS=$(aws rds describe-db-instances \
    --db-instance-identifier "${NEW_INSTANCE_NAME}" \
    --query 'DBInstances[0].DBInstanceStatus' \
    --output text 2>/dev/null || echo "not-found")

  if [ "${STATUS}" == "not-found" ]; then
    echo "Waiting for instance to be created..."
    sleep 10
    continue
  fi

  echo "Current status: ${STATUS}"

  if [ "${STATUS}" == "available" ]; then
    echo "Instance is now available!"
    break
  elif [ "${STATUS}" == "failed" ]; then
    echo "Instance restoration failed. Please check the AWS console for details."
    exit 1
  fi

  echo "Waiting 30 seconds before checking again..."
  sleep 30
done

# Get and display the endpoint information
ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier "${NEW_INSTANCE_NAME}" \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

PORT=$(aws rds describe-db-instances \
  --db-instance-identifier "${NEW_INSTANCE_NAME}" \
  --query 'DBInstances[0].Endpoint.Port' \
  --output text)

echo ""
echo "==================================================="
echo "Restoration complete!"
echo "Database endpoint: ${ENDPOINT}"
echo "Database port: ${PORT}"
echo "==================================================="
