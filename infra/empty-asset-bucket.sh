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

# Delete bucket with all objects!
aws s3 rb "s3://${bucket_name}" --force

echo "Bucket ${bucket_name} has been deleted."
