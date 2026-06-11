env := $(shell ./infra/get_env.sh)

ifeq ($(env),sandbox)
	DOMAIN_NAME := $(USER)-sandbox-web.ustaxcourt.gov
else ifeq ($(env),local)
	DOMAIN_NAME := localhost:8000
else
	DOMAIN_NAME := $(env)-web.ustaxcourt.gov
endif

check-env-is-aws:
	@if [ $(env) = "local" ]; then \
		echo "Environment is: 'localhost'.\nError: Not connected to AWS environment."; \
		exit 1; \
	else \
		echo "Environment is (AWS): '$(env)'.";\
	fi

# this command is used to setting up the bastion ssh keys and the aws secret manager secrets
# that will be used for the terraform setup during the ci/cd pipeline
aws-setup: check-env-is-aws aws-init
	@echo "Setting up AWS environment for $(env)..."

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

	@SECRET_STRING='{ \
		"DATABASE_PASSWORD": "'"$$(head -c 20 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 20)"'", \
		"BASTION_PUBLIC_KEY": "'"$$(cat ~/.ssh/wagtail_$(env)_bastion_key_id_rsa.pub.base64)"'", \
		"BASTION_PRIVATE_KEY": "'"$$(cat ~/.ssh/wagtail_$(env)_bastion_key_id_rsa.base64)"'", \
		"DJANGO_SUPERUSER_PASSWORD": "MISSING_CONFIG_AT_WEBSITE_SECRETS", \
		"DOMAIN_NAME": "$(DOMAIN_NAME)", \
		"SECRET_KEY": "'"$$(head -c 50 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' | head -c 50)"'", \
		"SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY": "MISSING_CONFIG_AT_WEBSITE_SECRETS_USED_FOR_SSO", \
		"SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET": "MISSING_CONFIG_AT_WEBSITE_SECRETS_USED_FOR_SSO", \
		"SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID": "MISSING_CONFIG_AT_WEBSITE_SECRETS_USED_FOR_SSO", \
		"DATABASE_HOSTNAME": "MISSING_CONFIG_AT_WEBSITE_SECRETS_USED_FOR_DB_RECOVERY", \
		"BASTION_HOST_IP": "MISSING_CONFIG_AT_WEBSITE_SECRETS_USED_FOR_DB_RECOVERY", \
		"USERS_TO_PREREGISTER": "MISSING_CONFIG_AT_WEBSITE_SECRETS", \
		"USERS_TO_PREREGISTER_PASSWORD": "MISSING_CONFIG_AT_WEBSITE_SECRETS", \
		"WAGTAILTRANSFER_SECRET_KEY": "'"$$(head -c 50 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' | head -c 50)"'", \
		"WAGTAILTRANSFER_SOURCES": "{}" \
	}'; \
	if aws secretsmanager describe-secret --secret-id website_secrets --region us-east-1 > /dev/null 2>&1; then \
		echo "Secret exists. Updating secret..."; \
		aws secretsmanager update-secret --secret-id website_secrets --region us-east-1 --secret-string "$$SECRET_STRING"; \
	else \
		echo "Creating new secret..."; \
		aws secretsmanager create-secret --name website_secrets --region us-east-1 --description "Secrets for website infrastructure" --secret-string "$$SECRET_STRING"; \
	fi

	@if aws iam get-user --user-name deployer > /dev/null 2>&1; then \
		echo "User 'deployer' already exists."; \
	else \
		echo "Creating user 'deployer'..."; \
		aws iam create-user --user-name deployer; \
	fi

	@POLICY_ARN=$$(aws iam list-policies --query "Policies[?PolicyName=='deployer-policy'].Arn" --output text); \
	if [ -n "$$POLICY_ARN" ]; then \
		echo "Policy 'deployer-policy' already exists."; \
	else \
		echo "Creating policy 'deployer-policy'..."; \
		aws iam create-policy --policy-name deployer-policy --policy-document file://./infra/iam/deployer-policy.json; \
		POLICY_ARN=$$(aws iam list-policies --query "Policies[?PolicyName=='deployer-policy'].Arn" --output text); \
	fi;\
	aws iam create-policy-version --policy-arn "$$POLICY_ARN" --policy-document file://./infra/iam/deployer-policy.json --set-as-default;\
	aws iam attach-user-policy --user-name deployer --policy-arn "$$POLICY_ARN";

	aws iam create-access-key --user-name deployer > ./infra/iam/$(env)_generated-deployer-access-key.json || true

# this command is used to setting up the bastion ssh keys and the aws secret manager secrets
# that will be used for the terraform setup during the ci/cd pipeline
aws-setup-wagtail-transfer: check-env-is-aws aws-init
	@echo "Setting up AWS environment for $(env)..."

	@if aws secretsmanager describe-secret --secret-id website_secrets --region us-east-1 > /dev/null 2>&1; then \
		echo "Secret 'website_secrets' exists. Setting Wagtail Transfer keys to default values if they do not exist..."; \
		SECRET_STRING=$$(aws secretsmanager get-secret-value --secret-id website_secrets --query SecretString --output text | jq 'if has("WAGTAILTRANSFER_SOURCES") then .["WAGTAILTRANSFER_SOURCES"] = .["WAGTAILTRANSFER_SOURCES"] else .["WAGTAILTRANSFER_SOURCES"] = "{}" end' | jq 'if has("WAGTAILTRANSFER_SECRET_KEY") then .["WAGTAILTRANSFER_SECRET_KEY"] = .["WAGTAILTRANSFER_SECRET_KEY"] else .["WAGTAILTRANSFER_SECRET_KEY"] = "'"$$(head -c 50 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' | head -c 50)"'" end'); \
		aws secretsmanager update-secret --secret-id website_secrets --region us-east-1 --secret-string "$$SECRET_STRING"; \
	else \
		echo "Secret 'website_secrets' does not exist. Run 'aws-setup' instead."; \
	fi

init:
	@echo "Initializing environment: $(env)"
	@cd infra && ./local_init.sh

aws-init: check-env-is-aws
	@echo "Initializing environment: $(env)"
	@cd infra && ./init.sh && \
	   . ./load-secrets.sh && \
	   if [ -n "$$BASTION_PUBLIC_KEY" ] && [ -n "$$BASTION_PRIVATE_KEY" ]; then \
		 echo "$$BASTION_PUBLIC_KEY" > ~/.ssh/wagtail_$(env)_bastion_key_id_rsa.pub.base64; \
		 echo "$$BASTION_PRIVATE_KEY" > ~/.ssh/wagtail_$(env)_bastion_key_id_rsa.base64; \
	   fi

create-db-restore: check-env-is-aws
	@echo "Creating database restore for environment: $(env)"
	@if [ -z "$(db_instance_id)" ] || [ -z "$(db_snapshot_id)" ]; then \
		echo "Error: db_instance_id and db_snapshot_id must be present.\n\nUsage:\nmake create-db-restore db_instance_id=<instance> db_snapshot_id=<snapshot>"; \
		exit 1; \
	fi
	@cd infra && ENVIRONMENT=$(env) ./restore-rds.sh $(db_instance_id) $(db_snapshot_id)

start-tunnel: check-env-is-aws
	@echo "Starting SSH tunnel to bastion host..."
	@cd infra && ENVIRONMENT=$(env) ./ssh-tunnel.sh

ecs-ssh:
	. ./.venv/bin/activate && cd infra && python3 ./scripts/ecs_ssh.py

apply-db-restore: check-env-is-aws
	@echo "Restoring database for environment: $(env)"
	@cd infra && ENVIRONMENT=$(env) ./apply-migrations-to-restored-db.sh

deploy: check-env-is-aws
	@echo "Deploying to environment: $(env)"
	cd infra && rm -rf .terraform && ENVIRONMENT=$(env) ./init.sh
	cd infra && ENVIRONMENT=$(env) ./deploy.sh

destroy: check-env-is-aws
	@echo "Destroying environment: $(env)"
	cd infra && ENVIRONMENT=$(env) ./destroy.sh

tag:
	git push
	git tag -f $(tag)
	git push -f origin $(tag)

restore: check-env-is-aws
	@echo "Restoring secrets in AWS environment: $(env)"
	aws secretsmanager restore-secret --secret-id website_secrets

aws-teardown: destroy
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

role: check-env-is-aws
	@echo "Attaching 'deployer-policy' to role: github-workflow-deployer..."
	@ACCOUNT_ID=$$(aws sts get-caller-identity --query Account --output text); \
	aws iam attach-role-policy \
	  --role-name github-workflow-deployer \
	  --policy-arn arn:aws:iam::$$ACCOUNT_ID:policy/deployer-policy
	@echo "... Waiting 3 seconds for IAM policy to propagate."
	@sleep 3
	@echo "Current attached policies:"
	@aws iam list-attached-role-policies --role-name github-workflow-deployer \
	  --query 'AttachedPolicies[*].[PolicyName, PolicyArn]' --output text | \
	  awk '{printf "%s: %s\n", $$1, $$2}'

test-e2e:
	@$(MAKE) -C website test-e2e args="$(args)"

test-voiceover:
	@$(MAKE) -C website test-voiceover baseUrl="$(baseUrl)"

setup-voiceover:
	@$(MAKE) -C website setup-voiceover

cypress-open:
	@$(MAKE) -C website cypress-open args="$(args)"

test-e2e-aws:
	@$(MAKE) -C website test-e2e-aws aws_env="$(aws_env)" sandbox_name="$(sandbox_name)" base_url="$(base_url)" secret_id="$(secret_id)" region="$(region)" spec="$(spec)" browser="$(browser)" args="$(args)" admin_username="$(admin_username)" admin_password="$(admin_password)"

cypress-open-aws:
	@$(MAKE) -C website cypress-open-aws aws_env="$(aws_env)" sandbox_name="$(sandbox_name)" base_url="$(base_url)" secret_id="$(secret_id)" region="$(region)" spec="$(spec)" browser="$(browser)" args="$(args)" admin_username="$(admin_username)" admin_password="$(admin_password)"

run:
	@$(MAKE) -C website run

reset:
	@$(MAKE) -C website reset

resetdb:
	@$(MAKE) -C website resetdb

makemigrations:
	@$(MAKE) -C website makemigrations

migrate:
	@$(MAKE) -C website migrate

check:
	@$(MAKE) -C website check

pytest:
	@$(MAKE) -C website pytest

aws-cypress-set-credentials:
	@ADMIN_USERNAME_VALUE="$(or $(ADMIN_USERNAME),$(admin_username))"; \
	ADMIN_PASSWORD_VALUE="$(ADMIN_PASSWORD)"; \
	if ! command -v aws >/dev/null 2>&1; then \
		echo "Error: aws CLI is required for aws-cypress-set-credentials."; \
		exit 1; \
	fi; \
	if ! command -v jq >/dev/null 2>&1; then \
		echo "Error: jq is required for aws-cypress-set-credentials."; \
		exit 1; \
	fi; \
	if [ -z "$$ADMIN_USERNAME_VALUE" ]; then \
		echo "Usage: ADMIN_USERNAME=<user> ADMIN_PASSWORD=<pass> make aws-cypress-set-credentials"; \
		echo "       Or omit ADMIN_PASSWORD to be prompted securely."; \
		echo "       Optionally add: secret_id=<name> region=<aws-region>"; \
		exit 1; \
	fi; \
	if [ -z "$$ADMIN_PASSWORD_VALUE" ]; then \
		printf "Admin password: "; \
		trap 'stty echo' EXIT INT TERM; \
		stty -echo; \
		IFS= read -r ADMIN_PASSWORD_VALUE; \
		stty echo; \
		trap - EXIT INT TERM; \
		printf '\n'; \
	fi; \
	if [ -z "$$ADMIN_PASSWORD_VALUE" ]; then \
		echo "Error: admin password is required."; \
		exit 1; \
	fi; \
	echo "Writing CYPRESS_ADMIN_USERNAME / CYPRESS_ADMIN_PASSWORD to secret '$(or $(secret_id),website_secrets)' in $(or $(region),us-east-1)..."; \
	SECRET=$$(aws secretsmanager get-secret-value \
		--secret-id "$(or $(secret_id),website_secrets)" \
		--region "$(or $(region),us-east-1)" \
		--query SecretString --output text); \
	UPDATED=$$(printf '%s' "$$SECRET" | jq \
		--arg u "$$ADMIN_USERNAME_VALUE" \
		--arg p "$$ADMIN_PASSWORD_VALUE" \
		'. + {CYPRESS_ADMIN_USERNAME: $$u, CYPRESS_ADMIN_PASSWORD: $$p}'); \
	aws secretsmanager update-secret \
		--secret-id "$(or $(secret_id),website_secrets)" \
		--region "$(or $(region),us-east-1)" \
		--secret-string "$$UPDATED"
	@echo "Done. Re-run your test-e2e-aws command — credentials will be picked up automatically."
