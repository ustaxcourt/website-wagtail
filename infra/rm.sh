#!/bin/bash

# this script can be used for removing resources from terraform state.
# you often will need to do this if you create a resource outside of terraform
# which you once had defined in terraform.

. ./setup.sh

resource=$1

terraform state rm "${resource}"
