#!/bin/bash

export AWS_PAGER=""
bucket_name="${ENVIRONMENT}-ustc-website-assets"

if [ "${ENVIRONMENT}" = "sandbox" ]; then
    bucket_name="${DOMAIN_NAME%-web.ustaxcourt.gov}-ustc-website-assets"
fi

# Check if bucket exists
if aws s3 ls "s3://${bucket_name}" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Bucket ${bucket_name} does not exist"
    exit 0
fi

echo "Found bucket: ${bucket_name}"

# Get object keys, handle empty buckets
objectKeys=$(aws s3api list-objects \
    --bucket "${bucket_name}" \
    --output json \
    --region us-east-1 | jq -r '.Contents[]?.Key // empty')

if [ -z "$objectKeys" ]; then
    echo "No objects found in the bucket"
    return 0
fi

# Delete each object concurrently
echo "$objectKeys" | xargs -P 10 -I {} bash -c '
    echo "Deleting: {}"
    aws s3api delete-object --bucket "'"$bucket_name"'" --key "{}" --region us-east-1
'

echo "Bucket cleanup complete"
