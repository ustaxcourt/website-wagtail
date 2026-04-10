#!/usr/bin/env python3
"""
Script to add a user email to a USERS_TO_PREREGISTER group in website_secrets.

Usage:
    python3 add_preregister_user.py <profile_name> <email> [<group_name>]

Example:
    python3 add_preregister_user.py sandbox user@ustaxcourt.gov
    python3 add_preregister_user.py sandbox user@ustaxcourt.gov Editors
    python3 add_preregister_user.py production user@ustaxcourt.gov Moderators

Requirements:
    pip install boto3
"""

import json
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

DEFAULT_GROUP = "Editors"


def add_preregister_user(profile_name: str, email: str, group_name: str) -> bool:
    """
    Add an email address to a USERS_TO_PREREGISTER group in website_secrets.

    Args:
        profile_name: AWS profile name configured in ~/.aws/config or ~/.aws/credentials
        email: Email address to add
        group_name: Group name within USERS_TO_PREREGISTER (e.g. "Editors", "Moderators")

    Returns:
        True if successful, False otherwise
    """
    try:
        session = boto3.Session(profile_name=profile_name)
        client = session.client("secretsmanager", region_name="us-east-1")

        response = client.get_secret_value(SecretId="website_secrets")
        secret = json.loads(response["SecretString"])

        users_to_preregister = json.loads(secret.get("USERS_TO_PREREGISTER", "{}"))

        if group_name not in users_to_preregister:
            print(f"Group '{group_name}' not found in USERS_TO_PREREGISTER")
            print(f"Available groups: {list(users_to_preregister.keys())}")
            return False

        group = users_to_preregister[group_name]

        if email in group:
            print(f"'{email}' is already in {group_name}")
            return True

        group.append(email)
        secret["USERS_TO_PREREGISTER"] = json.dumps(users_to_preregister)

        client.update_secret(
            SecretId="website_secrets", SecretString=json.dumps(secret)
        )
        print(f"Successfully added '{email}' to {group_name}")
        return True

    except ProfileNotFound:
        print(f"AWS profile '{profile_name}' not found.")
        print("Available profiles can be listed with: aws configure list-profiles")
        return False

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceNotFoundException":
            print(f"Secret 'website_secrets' not found using profile '{profile_name}'")
        elif error_code == "AccessDeniedException":
            print(
                f"Access denied when trying to access secret using profile '{profile_name}'"
            )
            print("Make sure the profile has proper permissions for SecretsManager")
        else:
            print(f"AWS error with profile '{profile_name}': {e}")
        return False

    except NoCredentialsError:
        print(f"No credentials found for profile '{profile_name}'.")
        print("Make sure the profile is properly configured in ~/.aws/credentials")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main():
    """Main function to parse arguments and add the user."""
    args = sys.argv[1:]

    if len(args) < 2 or len(args) > 3:
        print(
            "Usage: python3 add_preregister_user.py <profile_name> <email> [<group_name>]"
        )
        print("Example: python3 add_preregister_user.py sandbox user@ustaxcourt.gov")
        print(
            "         python3 add_preregister_user.py sandbox user@ustaxcourt.gov Editors"
        )
        print(
            "         python3 add_preregister_user.py production user@ustaxcourt.gov Moderators"
        )
        print()
        print(
            f"Adds an email address to a USERS_TO_PREREGISTER group (default: {DEFAULT_GROUP})"
        )
        print("in website_secrets in AWS Secrets Manager.")
        print()
        print("Available profiles can be listed with: aws configure list-profiles")
        sys.exit(0)

    profile_name = args[0]
    email = args[1]
    group_name = args[2] if len(args) == 3 else DEFAULT_GROUP

    if not profile_name.strip():
        print("Profile name cannot be empty")
        sys.exit(0)

    if not email.strip():
        print("Email address cannot be empty")
        sys.exit(0)

    if not group_name.strip():
        print("Group name cannot be empty")
        sys.exit(0)

    success = add_preregister_user(profile_name, email, group_name)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
