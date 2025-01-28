#!/bin/bash

ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text 2>/dev/null)

case "$ACCOUNT_ID" in
    "640168411491") echo "dev";;
    "202533521356") echo "test";;
    "221082179478") echo "sandbox";; # Sree
    "047719633139") echo "sandbox";; # Cody
    "354918408861") echo "sandbox";; # Miriam
    "890742592290") echo "sandbox";; # Joe
    "961341527731") echo "sandbox";; # Jim
    "039612867883") echo "sandbox";; # Tejha
    *) echo "unknown";;
esac
