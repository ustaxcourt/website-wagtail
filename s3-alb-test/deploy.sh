#!/bin/bash

pushd lambda
  npm install && zip -r lambda_function.zip index.js node_modules
popd

terraform init
terraform apply --auto-approve

BUCKET_NAME=$(terraform output -raw s3_bucket_name)

aws s3 sync ./static s3://$BUCKET_NAME
