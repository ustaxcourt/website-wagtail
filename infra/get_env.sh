#!/bin/bash

ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text 2>/dev/null)

case "$ACCOUNT_ID" in
    "640168411491") echo "dev";;
    "202533521356") echo "test";;
    "221082179478") echo "sandbox";;
    "047719633139") echo "cody";;
    *) echo "unknown";;
esac
