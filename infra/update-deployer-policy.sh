#!/bin/bash

set -euo pipefail

POLICY_NAME="deployer-policy"
POLICY_FILE="./iam/deployer-policy.json"
USER_NAME="deployer"

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
        aws iam create-policy-version --policy-arn "$POLICY_ARN" \
            --policy-document file://"$POLICY_FILE" --set-as-default

        echo "Cleaning up old versions if more than 4 exist..."
        VERSIONS=$(aws iam list-policy-versions --policy-arn "$POLICY_ARN" \
            --query "Versions[?IsDefaultVersion==\`false\`] | [].[VersionId]" --output text)

        COUNT=0
        for v in $VERSIONS; do
            COUNT=$((COUNT + 1))
        done

        if [ "$COUNT" -ge 4 ]; then
            # Delete oldest non-default version
            OLDEST=$(aws iam list-policy-versions --policy-arn "$POLICY_ARN" \
                --query "Versions[?IsDefaultVersion==\`false\`] | sort_by(@, &CreateDate) | [0].VersionId" \
                --output text)

            echo "Deleting oldest policy version: $OLDEST"
            aws iam delete-policy-version --policy-arn "$POLICY_ARN" --version-id "$OLDEST"
        fi
    fi
else
    echo "Creating new policy '$POLICY_NAME'..."
    POLICY_ARN=$(aws iam create-policy --policy-name "$POLICY_NAME" \
        --policy-document file://"$POLICY_FILE" --query "Policy.Arn" --output text)
fi

echo "Ensuring policy is attached to user '$USER_NAME'..."
aws iam attach-user-policy --user-name "$USER_NAME" --policy-arn "$POLICY_ARN"

echo "Policy '$POLICY_NAME' is up-to-date and attached to user '$USER_NAME'."
