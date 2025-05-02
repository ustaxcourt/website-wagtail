#!/bin/bash

set -euo pipefail

POLICY_NAME="deployer-policy"
POLICY_FILE="./iam/deployer-policy.json"
USER_NAME="deployer"
MAX_VERSIONS=5 # AWS limit for IAM policy versions

echo "Checking if IAM policy '$POLICY_NAME' exists..."

POLICY_ARN=$(aws iam list-policies --scope Local --query "Policies[?PolicyName=='${POLICY_NAME}'].Arn" --output text)

if [ -n "$POLICY_ARN" ]; then
    echo "Policy '$POLICY_NAME' exists with ARN: $POLICY_ARN"

    # Get the latest version ID
    VERSION_ID=$(aws iam list-policy-versions --policy-arn "$POLICY_ARN" \
        --query "Versions[?IsDefaultVersion==\`true\`].VersionId" --output text)

    echo "Fetching current policy document from AWS..."
    aws iam get-policy-version --policy-arn "$POLICY_ARN" --version-id "$VERSION_ID" \
        --query "PolicyVersion.Document" --output json > /tmp/aws_policy.json

    echo "Normalizing local policy document for comparison..."
    jq -S . "$POLICY_FILE" > /tmp/local_policy.json

    # Remove metadata fields from AWS policy document (like Version, CreateDate, VersionId, etc.)
    jq 'del(.Version, .CreateDate, .VersionId, .IsDefaultVersion)' /tmp/aws_policy.json > /tmp/aws_policy_normalized.json

    # Remove metadata fields from local policy document
    jq 'del(.Version)' /tmp/local_policy.json > /tmp/local_policy_normalized.json

    # Sort keys within each statement (to ensure they are in the same order for comparison)
    jq '.Statement |= map(to_entries | sort_by(.key) | from_entries)' /tmp/aws_policy_normalized.json > /tmp/aws_policy_sorted.json
    jq '.Statement |= map(to_entries | sort_by(.key) | from_entries)' /tmp/local_policy_normalized.json > /tmp/local_policy_sorted.json

    echo "Comparing local and AWS policy documents..."
    if cmp -s /tmp/aws_policy_sorted.json /tmp/local_policy_sorted.json; then
        echo "Policy is up-to-date. No changes needed."
    else
        echo "Policy differs. Creating a new version..."

        echo "Checking number of existing policy versions..."
        VERSION_INFO=$(aws iam list-policy-versions --policy-arn "$POLICY_ARN" --output json)
        VERSION_COUNT=$(echo "$VERSION_INFO" | jq '.Versions | length')

        if [ "$VERSION_COUNT" -ge "$MAX_VERSIONS" ]; then
            echo "Maximum number of versions ($MAX_VERSIONS) reached. Deleting the oldest non-default version."

            # Find the VersionId of the oldest non-default version
            OLDEST_NON_DEFAULT_VERSION_ID=$(echo "$VERSION_INFO" | jq -r \
                '.Versions | map(select(.IsDefaultVersion == false)) | sort_by(.CreateDate) | .[0].VersionId // empty')

            if [ -n "$OLDEST_NON_DEFAULT_VERSION_ID" ]; then
                 echo "Deleting oldest non-default policy version: $OLDEST_NON_DEFAULT_VERSION_ID"
                 if ! aws iam delete-policy-version --policy-arn "$POLICY_ARN" --version-id "$OLDEST_NON_DEFAULT_VERSION_ID"; then
                     echo "Error: Failed to delete policy version $OLDEST_NON_DEFAULT_VERSION_ID. Exiting."
                     exit 1
                 fi
                 echo "Successfully deleted version $OLDEST_NON_DEFAULT_VERSION_ID."
            else
                 echo "Warning: Could not find an old non-default version to delete, even though count is >= $MAX_VERSIONS. This might indicate an unexpected state."
                 # Decide if you want to proceed or exit here. Proceeding might still fail.
                 # For safety, let's exit
                 echo "Exiting due to inability to find a deletable version."
                 exit 1
            fi
        else
             echo "Current version count ($VERSION_COUNT) is less than maximum ($MAX_VERSIONS). No cleanup needed before creating new version."
        fi

        aws iam create-policy-version --policy-arn "$POLICY_ARN" \
            --policy-document file://"$POLICY_FILE" --set-as-default

    fi
else
    echo "Creating new policy '$POLICY_NAME'..."
    POLICY_ARN=$(aws iam create-policy --policy-name "$POLICY_NAME" \
        --policy-document file://"$POLICY_FILE" --query "Policy.Arn" --output text)
fi

echo "Ensuring policy is attached to user '$USER_NAME'..."
aws iam attach-user-policy --user-name "$USER_NAME" --policy-arn "$POLICY_ARN"

echo "Policy '$POLICY_NAME' is up-to-date and attached to user '$USER_NAME'."
