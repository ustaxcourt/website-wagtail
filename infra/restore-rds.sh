#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration and Argument Parsing ---

# Function to display usage instructions
usage() {
  echo "Usage: $0 <source-instance-id> <snapshot-id>"
  echo "  <source-instance-id>: The identifier of the RDS instance whose configuration (VPC SG, Subnet Group, etc.) will be used."
  echo "  <snapshot-id>:        The identifier of the RDS snapshot to restore from."
  exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  usage
fi

# Assign arguments to variables
SOURCE_INSTANCE_ID="$1"
SNAPSHOT_ID="$2"
NEW_INSTANCE_NAME="$1-restored"

# --- Dependency Checks ---

echo "Checking dependencies..."
command -v aws >/dev/null 2>&1 || { echo >&2 "Error: AWS CLI ('aws') not found. Please install it and configure credentials. Aborting."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo >&2 "Error: 'jq' not found. Please install it (e.g., 'sudo apt-get install jq' or 'brew install jq'). Aborting."; exit 1; }
echo "Dependencies found."
echo ""

# --- Pre-existence Check for Target Instance ---

echo "Checking if target instance '${NEW_INSTANCE_NAME}' already exists..."
EXISTING_STATUS=$(aws rds describe-db-instances --db-instance-identifier "${NEW_INSTANCE_NAME}" --query 'DBInstances[0].DBInstanceStatus' --output text 2>/dev/null || echo "not-found")

if [ "${EXISTING_STATUS}" != "not-found" ]; then
  echo >&2 "Error: An RDS instance named '${NEW_INSTANCE_NAME}' already exists with status '${EXISTING_STATUS}'. Aborting."
  exit 1
fi
echo "Target instance '${NEW_INSTANCE_NAME}' does not exist. Proceeding."
echo ""

# --- Get Source Instance Configuration ---

echo "Fetching configuration from source instance '${SOURCE_INSTANCE_ID}'..."
# Use error suppression and check exit code for source instance existence
if ! INSTANCE_INFO=$(aws rds describe-db-instances --db-instance-identifier "${SOURCE_INSTANCE_ID}" --output json 2>/dev/null); then
    echo >&2 "Error: Could not retrieve information for source instance '${SOURCE_INSTANCE_ID}'. Check if the instance exists and you have permissions."
    exit 1
fi

# Check if the describe-db-instances command returned data
if [ -z "${INSTANCE_INFO}" ] || [ "$(echo "${INSTANCE_INFO}" | jq '.DBInstances | length')" -eq 0 ]; then
    echo >&2 "Error: No data returned for source instance '${SOURCE_INSTANCE_ID}'. Check instance identifier and permissions."
    exit 1
fi

# Extract necessary values using jq, with error checking
VPC_SECURITY_GROUP_ID=$(echo "${INSTANCE_INFO}" | jq -r '.DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId // empty')
DB_SUBNET_GROUP=$(echo "${INSTANCE_INFO}" | jq -r '.DBInstances[0].DBSubnetGroup.DBSubnetGroupName // empty')
AVAILABILITY_ZONE=$(echo "${INSTANCE_INFO}" | jq -r '.DBInstances[0].AvailabilityZone // empty')
STORAGE_TYPE=$(echo "${INSTANCE_INFO}" | jq -r '.DBInstances[0].StorageType // empty')
DB_INSTANCE_CLASS=$(echo "${INSTANCE_INFO}" | jq -r '.DBInstances[0].DBInstanceClass // empty')

# Validate extracted values
if [ -z "${VPC_SECURITY_GROUP_ID}" ]; then echo >&2 "Error: Could not extract VPC Security Group ID from source instance."; exit 1; fi
if [ -z "${DB_SUBNET_GROUP}" ]; then echo >&2 "Error: Could not extract DB Subnet Group Name from source instance."; exit 1; fi
if [ -z "${AVAILABILITY_ZONE}" ]; then echo >&2 "Error: Could not extract Availability Zone from source instance."; exit 1; fi
if [ -z "${STORAGE_TYPE}" ]; then echo >&2 "Error: Could not extract Storage Type from source instance."; exit 1; fi
if [ -z "${DB_INSTANCE_CLASS}" ]; then echo >&2 "Error: Could not extract DB Instance Class from source instance."; exit 1; fi

echo "Successfully fetched configuration:"
echo "  - VPC Security Group ID: ${VPC_SECURITY_GROUP_ID}"
echo "  - DB Subnet Group:       ${DB_SUBNET_GROUP}"
echo "  - Availability Zone:     ${AVAILABILITY_ZONE}"
echo "  - Storage Type:          ${STORAGE_TYPE}"
echo "  - Instance Class:        ${DB_INSTANCE_CLASS}"
echo ""

# --- Verify Snapshot Existence ---
echo "Verifying snapshot '${SNAPSHOT_ID}' exists..."
# Attempt to describe the snapshot. Suppress stderr and check the exit code.
if ! aws rds describe-db-snapshots --db-snapshot-identifier "${SNAPSHOT_ID}" --output text --query 'DBSnapshots[0].DBSnapshotIdentifier' > /dev/null 2>&1; then
    echo >&2 "Error: DBSnapshotNotFound: Snapshot '${SNAPSHOT_ID}' could not be found."
    echo >&2 "Please verify the snapshot identifier and region. Aborting."
    exit 1
fi
echo "Snapshot '${SNAPSHOT_ID}' found."
echo ""


# --- Restore RDS Instance ---

echo "Initiating restore of instance '${NEW_INSTANCE_NAME}' from snapshot '${SNAPSHOT_ID}'..."
# We already checked for snapshot existence, but the restore command itself can still fail for other reasons.
# The 'set -e' will cause the script to exit if this command fails.
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier "${NEW_INSTANCE_NAME}" \
  --db-snapshot-identifier "${SNAPSHOT_ID}" \
  --db-instance-class "${DB_INSTANCE_CLASS}" \
  --vpc-security-group-ids "${VPC_SECURITY_GROUP_ID}" \
  --db-subnet-group-name "${DB_SUBNET_GROUP}" \
  --availability-zone "${AVAILABILITY_ZONE}" \
  --no-publicly-accessible \
  --storage-type "${STORAGE_TYPE}" \
  --deletion-protection # Consider making this optional via an argument

echo "Restore command submitted."
echo ""

# --- Wait for Instance Availability ---

echo "Waiting for instance '${NEW_INSTANCE_NAME}' to become available (this may take several minutes)..."
if aws rds wait db-instance-available --db-instance-identifier "${NEW_INSTANCE_NAME}"; then
  echo "Instance '${NEW_INSTANCE_NAME}' is now available!"
else
  echo >&2 "Error: AWS waiter failed. The instance might be in a failed state or the wait timed out."
  echo >&2 "Please check the AWS RDS console for details on instance '${NEW_INSTANCE_NAME}'."
  # Optionally retrieve and display the final status here
  # aws rds describe-db-instances --db-instance-identifier "${NEW_INSTANCE_NAME}" --query 'DBInstances[0].DBInstanceStatus' --output text
  exit 1
fi
echo ""

# --- Get and Display Endpoint Information ---

echo "Fetching endpoint information for '${NEW_INSTANCE_NAME}'..."
ENDPOINT_INFO=$(aws rds describe-db-instances \
  --db-instance-identifier "${NEW_INSTANCE_NAME}" \
  --query 'DBInstances[0].Endpoint' \
  --output json)

ENDPOINT_ADDRESS=$(echo "${ENDPOINT_INFO}" | jq -r '.Address // empty')
ENDPOINT_PORT=$(echo "${ENDPOINT_INFO}" | jq -r '.Port // empty')

if [ -z "${ENDPOINT_ADDRESS}" ] || [ -z "${ENDPOINT_PORT}" ]; then
    echo >&2 "Warning: Could not retrieve endpoint details automatically. The instance might still be initializing or encountered an issue."
    echo >&2 "Please check the AWS console for endpoint details."
else
    echo ""
    echo "==================================================="
    echo " RDS Instance Restoration Complete!"
    echo "==================================================="
    echo " New Instance ID: ${NEW_INSTANCE_NAME}"
    echo " Source Snapshot: ${SNAPSHOT_ID}"
    echo " Database Endpoint: ${ENDPOINT_ADDRESS}"
    echo " Database Port: ${ENDPOINT_PORT}"
    echo "==================================================="
    echo ""
    echo "Note: Remember to manage the master password for the new instance if necessary."
    echo "The password will be the same as the snapshot's source instance unless modified."
fi

exit 0
