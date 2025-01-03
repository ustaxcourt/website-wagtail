env := $(shell ./infra/get_env.sh)

# this command is used to setting up the bastion ssh keys and the aws secret manager secrets
# that will be used for the terraform setup during the ci/cd pipeline
aws-setup:
	@if [ -z "$(DOMAIN_NAME)" ]; then \
		echo "Error: DOMAIN_NAME environment variable is not set"; \
		exit 1; \
	fi

	@if [ -f ~/.ssh/wagtail_$(env)_bastion_key_id_rsa ]; then \
		echo "Local SSH Key for environment '$(env)' already exists."; \
	else \
		cd ~/.ssh && ssh-keygen -f wagtail_$(env)_bastion_key_id_rsa -N ''; \
		cd ~/.ssh && cat wagtail_$(env)_bastion_key_id_rsa | base64 > wagtail_$(env)_bastion_key_id_rsa.base64; \
		cd ~/.ssh && cat wagtail_$(env)_bastion_key_id_rsa.pub | base64 > wagtail_$(env)_bastion_key_id_rsa.pub.base64; \
	fi

	@if aws secretsmanager describe-secret --secret-id website_secrets --region us-east-1 > /dev/null 2>&1; then \
		echo "Secret exists. Updating secret..."; \
		aws secretsmanager update-secret --secret-id website_secrets --region us-east-1 --secret-string '{ \
			"DATABASE_PASSWORD": "'"$$(head -c 20 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 20)"'", \
			"BASTION_PUBLIC_KEY": "'"$$(cat ~/.ssh/wagtail_$(env)_bastion_key_id_rsa.pub.base64)"'", \
			"BASTION_PRIVATE_KEY": "'"$$(cat ~/.ssh/wagtail_$(env)_bastion_key_id_rsa.base64)"'", \
			"SUPERUSER_PASSWORD": "ustcAdminPW!", \
			"DOMAIN_NAME": "$(DOMAIN_NAME)", \
			"SECRET_KEY": "'"$$(head -c 50 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' | head -c 50)"'" \
		}'; \
	else \
		echo "Creating new secret..."; \
		aws secretsmanager create-secret --name website_secrets --region us-east-1 --description "Secrets for website infrastructure" --secret-string '{ \
			"DATABASE_PASSWORD": "'"$$(head -c 20 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 20)"'", \
			"BASTION_PUBLIC_KEY": "'"$$(cat ~/.ssh/wagtail_$(env)_bastion_key_id_rsa.pub.base64)"'", \
			"BASTION_PRIVATE_KEY": "'"$$(cat ~/.ssh/wagtail_$(env)_bastion_key_id_rsa.base64)"'", \
			"SUPERUSER_PASSWORD": "ustcAdminPW!", \
			"DOMAIN_NAME": "$(DOMAIN_NAME)", \
			"SECRET_KEY": "'"$$(head -c 50 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' | head -c 50)"'" \
		}'; \
	fi

	@if aws iam get-user --user-name deployer > /dev/null 2>&1; then \
		echo "User 'deployer' already exists."; \
	else \
		echo "Creating user 'deployer'..."; \
		aws iam create-user --user-name deployer; \
	fi

	@if aws iam list-policies --query "Policies[?PolicyName=='deployer-policy']" --output text | grep -q 'deployer-policy'; then \
		echo "Policy 'deployer-policy' already exists."; \
	else \
		echo "Creating policy 'deployer-policy'..."; \
		aws iam create-policy --policy-name deployer-policy --policy-document file://./infra/iam/deployer-policy.json; \
	fi

	aws iam attach-user-policy --user-name deployer --policy-arn "$$(aws iam list-policies --query "Policies[?PolicyName=='deployer-policy'].Arn" --output text)"
	aws iam create-access-key --user-name deployer > ./infra/iam/$(env)_generated-deployer-access-key.json || true

init:
	cd infra && ./init.sh

deploy:
	@echo "Deploying to environment: $(env)"
	cd infra && rm -rf .terraform && ENVIRONMENT=$(env) ./init.sh
	cd infra && ENVIRONMENT=$(env) ./deploy.sh

destroy:
	@echo "Destroying environment: $(env)"
	cd infra && ENVIRONMENT=$(env) ./destroy.sh

tag:
	git tag -f $(tag)
	git push -f origin $(tag)

teardown: destroy
	@echo "Cleaning up..."

	# Delete the secret if it exists
	@if aws secretsmanager describe-secret --secret-id website_secrets --region us-east-1 > /dev/null 2>&1; then \
		aws secretsmanager delete-secret --secret-id website_secrets --region us-east-1 --force-delete-without-recovery; \
		echo ".... Secrets deleted."; \
	else \
		echo ".... Secret 'website_secrets' does not exist."; \
	fi

	# Detach the policy if it exists
	@POLICY_ARN=$$(aws iam list-policies --query "Policies[?PolicyName=='deployer-policy'].Arn" --output text); \
	if [ -n "$$POLICY_ARN" ]; then \
		aws iam detach-user-policy --user-name deployer --policy-arn "$$POLICY_ARN"; \
		echo ".... Policy detached."; \
	else \
		echo ".... Policy 'deployer-policy' does not exist."; \
	fi

	# Delete the policy if it exists
	@if [ -n "$$POLICY_ARN" ]; then \
		aws iam delete-policy --policy-arn "$$POLICY_ARN"; \
		echo ".... Policy deleted."; \
	else \
		echo ".... Policy 'deployer-policy' does not exist."; \
	fi

	# Delete all access keys for the deployer user
	@if aws iam get-user --user-name deployer > /dev/null 2>&1; then \
		ACCESS_KEY_IDS=$$(aws iam list-access-keys --user-name deployer --query 'AccessKeyMetadata[].AccessKeyId' --output text); \
		for KEY_ID in $$ACCESS_KEY_IDS; do \
			echo "Deleting access key $$KEY_ID..."; \
			aws iam delete-access-key --user-name deployer --access-key-id "$$KEY_ID"; \
		done; \
		echo ".... All access keys deleted."; \
	else \
		echo ".... User 'deployer' does not exist or has no access keys."; \
	fi

	# Delete the user if it exists
	@if aws iam get-user --user-name deployer > /dev/null 2>&1; then \
		aws iam delete-user --user-name deployer; \
		echo ".... User deleted."; \
	else \
		echo ".... User 'deployer' does not exist."; \
	fi

	# Remove the generated access key file
	@rm -f ./infra/iam/generated-deployer-access-key.json
	@echo ".... Cleaned up."
