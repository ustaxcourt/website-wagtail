#!/bin/bash

source ./setup.sh

terraform init \
    -upgrade \
    -backend=true \
    -backend-config=bucket="${STATE_BUCKET}" \
    -backend-config=key="${KEY}" \
    -backend-config=dynamodb_table="${LOCK_TABLE}" \
    -backend-config=region="${REGION}"

echo "Applying targeted update to Bastion Security Group..."
terraform apply -target=module.app.aws_instance.bastion -target=module.app.aws_security_group.bastion_sg -auto-approve

echo "Bastion Security Group update applied."

BASTION_HOST_IP=$(terraform output -raw bastion_public_ip)
if [ -z "${BASTION_HOST_IP}" ]; then
  echo "ERROR: terraform output 'bastion_public_ip' is empty. Check that terraform state is initialized."
  exit 1
fi

DATABASE_HOSTNAME=$(terraform output -raw database_endpoint)
if [ -z "${DATABASE_HOSTNAME}" ]; then
  echo "ERROR: terraform output 'database_endpoint' is empty. Check that terraform state is initialized."
  exit 1
fi

mkdir -p .ssh
echo "${BASTION_PRIVATE_KEY}" | base64 --decode > .ssh/id_rsa
chmod 600 .ssh/id_rsa
echo "Bastion private key configured."

echo "Waiting for bastion host to accept SSH connections..."
for i in $(seq 1 20); do
  if ssh-keyscan -H "${BASTION_HOST_IP}" > .ssh/known_hosts 2>/dev/null && [ -s .ssh/known_hosts ]; then
    echo "Host key scanned and added."
    break
  fi
  sleep 5
done

if [ ! -s .ssh/known_hosts ]; then
  echo "ERROR: ssh-keyscan failed for ${BASTION_HOST_IP} after waiting for boot"
  exit 1
fi

echo "Opening SSH tunnel. Connect in localhost:5432 ..."

ssh -o StrictHostKeyChecking=yes -o UserKnownHostsFile=.ssh/known_hosts \
    -L "5432:${DATABASE_HOSTNAME}" \
    -N -q -i .ssh/id_rsa "ubuntu@${BASTION_HOST_IP}" || {
      echo "ERROR: SSH tunnel command failed or was interrupted."
      exit 1;
    }

# This part of the script will only be reached AFTER you press Ctrl+C
# or if the SSH connection breaks for another reason.
echo "SSH tunnel closed."

exit 0
