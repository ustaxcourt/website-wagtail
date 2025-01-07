#!/bin/bash

export AWS_PAGER=""
bucket_name="${ENVIRONMENT}-ustc-website-assets"

# Check if bucket exists
if aws s3 ls "s3://${bucket_name}" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Bucket ${bucket_name} does not exist, continuing to run terraform destroy"
    exit 0
fi

echo "Found bucket: ${bucket_name}"
echo "Deleting all objects and directories..."

# First delete all versions and delete markers
aws s3api list-object-versions \
    --bucket "${bucket_name}" \
    --output json \
    --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}} + {Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' \
    --region us-east-1 | \
jq -r '.Objects[] | select(. != null) | [.Key, .VersionId] | @tsv' | \
while IFS=$'\t' read -r key version_id; do
    aws s3api delete-object \
        --bucket "${bucket_name}" \
        --key "$key" \
        --version-id "$version_id" \
        --region us-east-1
done

# List and delete all objects including those in subdirectories
aws s3api list-objects-v2 \
    --bucket "${bucket_name}" \
    --region us-east-1 \
    --query 'Contents[].{Key: Key}' \
    --output json | \
jq -r '.[] | .Key' | \
while read -r key; do
    if [ ! -z "$key" ]; then
        aws s3api delete-object \
            --bucket "${bucket_name}" \
            --key "$key" \
            --region us-east-1
    fi
done

# Force delete any remaining objects and their versions
aws s3 rm "s3://${bucket_name}" \
    --recursive \
    --force \
    --region us-east-1 \
    --include "*"

echo "Bucket cleanup complete"

exit 1;
