#!/bin/bash

export AWS_PAGER=""
bucket_name="${ENVIRONMENT}-ustc-website-assets"

# Check if bucket exists
if aws s3 ls "s3://${bucket_name}" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Bucket ${bucket_name} does not exist, continuing to run terraform destroy"
    return 0
fi

echo "Found bucket: ${bucket_name}"
echo "Deleting all objects..."

# Delete all versions and delete markers
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

# Delete remaining objects
aws s3 rm "s3://${bucket_name}" --recursive --region us-east-1

echo "Bucket cleanup complete"
