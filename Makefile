aws-setup:
	@if [ -f ~/.ssh/wagtail_bastion_key_id_rsa ]; then \
		echo "Key already exists"; \
	else \
		cd ~/.ssh && ssh-keygen -f wagtail_bastion_key_id_rsa -N ''; \
		cd ~/.ssh && cat wagtail_bastion_key_id_rsa | base64 > wagtail_bastion_key_id_rsa.base64; \
		cd ~/.ssh && cat wagtail_bastion_key_id_rsa.pub | base64 > wagtail_bastion_key_id_rsa.pub.base64; \
	fi
	@if aws secretsmanager describe-secret --secret-id website_secrets --region us-east-1 > /dev/null 2>&1; then \
		echo "Secret exists. Updating secret..."; \
		aws secretsmanager update-secret --secret-id website_secrets --region us-east-1 --secret-string '{ \
			"DATABASE_PASSWORD": "your_database_password_here", \
			"BASTION_PUBLIC_KEY": "'"$$(cat ~/.ssh/wagtail_bastion_key_id_rsa.pub.base64)"'", \
			"BASTION_PRIVATE_KEY": "'"$$(cat ~/.ssh/wagtail_bastion_key_id_rsa.base64)"'", \
			"SUPERUSER_PASSWORD": "your_superuser_password_here", \
			"SECRET_KEY": "your_superuser_password_here" \
		}'; \
	else \
		echo "Creating new secret..."; \
		aws secretsmanager create-secret --name website_secrets --region us-east-1 --description "Secrets for website infrastructure" --secret-string '{ \
			"DATABASE_PASSWORD": "your_database_password_here", \
			"BASTION_PUBLIC_KEY": "'"$$(cat ~/.ssh/wagtail_bastion_key_id_rsa.pub.base64)"'", \
			"BASTION_PRIVATE_KEY": "'"$$(cat ~/.ssh/wagtail_bastion_key_id_rsa.base64)"'", \
			"SUPERUSER_PASSWORD": "your_superuser_password_here", \
			"SECRET_KEY": "your_superuser_password_here" \
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
	aws iam create-access-key --user-name deployer > ./infra/iam/generated-deployer-access-key.json

env-setup:

# clean:
# 	@echo "Cleaning up..."
# 	@aws secretsmanager delete-secret --secret-id website_secrets --region us-east-1
# 	@echo ".... Secrets deleted."
# 	@aws iam detach-user-policy --user-name deployer --policy-arn "$$(aws iam list-policies --query "Policies[?PolicyName=='deployer-policy'].Arn" --output text)" || true
# 	@echo ".... Policy detached."
# 	@aws iam delete-policy --policy-arn "$$(aws iam list-policies --query "Policies[?PolicyName=='deployer-policy'].Arn" --output text)" || true
# 	@echo ".... Policy deleted."
# 	@aws iam delete-access-key --user-name deployer --access-key-id "$$(jq -r '.AccessKey.AccessKeyId' ./infra/iam/generated-deployer-access-key.json)" || true
# 	@echo ".... Access key deleted."
# 	@aws iam delete-user --user-name deployer
# 	@echo ".... User deleted."
# 	@rm -rf ./infra/iam/generated-deployer-access-key.json
# 	@echo ".... Cleaned up."

clean:
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
