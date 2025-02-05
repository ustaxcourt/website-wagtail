#!/bin/bash

ACCOUNT_ALIAS=$(aws iam list-account-aliases --query 'AccountAliases'  --output text 2>/dev/null|| echo "localhost")

ENV="${ACCOUNT_ALIAS##*-}"

echo $ENV
