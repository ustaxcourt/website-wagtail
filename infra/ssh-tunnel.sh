#!/bin/bash

source ./setup.sh

source ./setup_zone.sh

./update-deployer-policy.sh

terraform init \
    -upgrade \
    -backend=true \
    -backend-config=bucket="${STATE_BUCKET}" \
    -backend-config=key="${KEY}" \
    -backend-config=dynamodb_table="${LOCK_TABLE}" \
    -backend-config=region="${REGION}"

terraform refresh

echo "Applying targeted update to Bastion Security Group..."
terraform apply -target=module.app.aws_security_group.bastion_sg -auto-approve

echo "Bastion Security Group update applied."

BASTION_HOST_IP=$(terraform output -raw bastion_public_ip)

mkdir -p .ssh
echo "${BASTION_PRIVATE_KEY}" | base64 --decode > .ssh/id_rsa
chmod 600 .ssh/id_rsa
echo "Bastion private key configured."

ssh-keyscan -H ${BASTION_HOST_IP} > .ssh/known_hosts || { echo "ERROR: ssh-keyscan failed for ${BASTION_HOST_IP}"; exit 1; }
echo "Host key scanned and added."

echo "SSH tunnel opened in background. Connect in localhost:5432 ..."

ssh -o StrictHostKeyChecking=yes -o UserKnownHostsFile=.ssh/known_hosts \
    -L 5432:${DATABASE_HOSTNAME}:5432 \
    -N -q -i .ssh/id_rsa ubuntu@${BASTION_HOST_IP} || {
      echo "ERROR: SSH tunnel command failed or was interrupted."
      exit 1;
    }

# This part of the script will only be reached AFTER you press Ctrl+C
# or if the SSH connection breaks for another reason.
echo "SSH tunnel closed."

exit 0
