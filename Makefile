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
			"SUPERUSER_PASSWORD": "your_superuser_password_here" \
		}'; \
	else \
		echo "Creating new secret..."; \
		aws secretsmanager create-secret --name website_secrets --region us-east-1 --description "Secrets for website infrastructure" --secret-string '{ \
			"DATABASE_PASSWORD": "your_database_password_here", \
			"BASTION_PUBLIC_KEY": "'"$$(cat ~/.ssh/wagtail_bastion_key_id_rsa.pub.base64)"'", \
			"BASTION_PRIVATE_KEY": "'"$$(cat ~/.ssh/wagtail_bastion_key_id_rsa.base64)"'", \
			"SUPERUSER_PASSWORD": "your_superuser_password_here" \
		}'; \
	fi

env-setup:
