#!/bin/bash
set -e

# List of JSON keys we want to handle
KEYS=(
  "DATABASE_PASSWORD"
  "BASTION_PUBLIC_KEY"
  "BASTION_PRIVATE_KEY"
  "DJANGO_SUPERUSER_PASSWORD"
  "WAGTAIL_EDITOR_PASSWORD"
  "WAGTAIL_MODERATOR_PASSWORD"
  "DOMAIN_NAME"
  "SECRET_KEY"
)

# If website_secrets doesn't exist, create a blank JSON file
if [ ! -f website_secrets ]; then
  echo "No 'website_secrets' file found. Creating a new one..."
  echo "{}" > website_secrets
fi

# For each key in KEYS, prompt user
for KEY in "${KEYS[@]}"; do
  # Extract current value from website_secrets (if it exists)
  CURRENT_VALUE=$(jq -r --arg KEY "$KEY" '.[$KEY] // ""' website_secrets)

  if [ -n "$CURRENT_VALUE" ]; then
    echo "Current value for $KEY: $CURRENT_VALUE"
  else
    echo "No current value for $KEY."
  fi

  # Prompt for new value; user can press Enter to keep current
  read -p "Enter new value for $KEY (or press Enter to keep current): " NEW_VALUE

  # If user entered a new value, update it
  if [ -n "$NEW_VALUE" ]; then
    jq --arg KEY "$KEY" --arg NEW_VALUE "$NEW_VALUE" \
      '.[$KEY] = $NEW_VALUE' website_secrets > website_secrets.tmp
    mv website_secrets.tmp website_secrets
    echo "Updated $KEY."
  else
    echo "Keeping existing $KEY."
  fi

  echo
done

echo "All secrets updated."
