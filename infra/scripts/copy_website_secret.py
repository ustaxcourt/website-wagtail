#!/usr/bin/env python3
"""
Script to copy a single property from website_secrets in one AWS account to another.

Usage:
    python3 copy_website_secret.py <source_profile> <destination_profile> <property_name> [--dry-run]

Example:
    python3 copy_website_secret.py production sandbox DATABASE_PASSWORD
    python3 copy_website_secret.py sandbox production SECRET_KEY --dry-run

Options:
    --dry-run    Show what the destination secret would look like without making changes

Requirements:
    pip install boto3
"""

import json
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from typing import Dict, Any, Optional


def get_secret_value(profile_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the website_secrets value from the specified AWS profile.

    Args:
        profile_name: AWS profile name configured in ~/.aws/config or ~/.aws/credentials

    Returns:
        Dictionary containing the secret data if successful, None otherwise
    """
    try:
        # Create session with the specified profile
        session = boto3.Session(profile_name=profile_name)
        client = session.client("secretsmanager", region_name="us-east-1")

        # Get current account info for logging
        try:
            sts_client = session.client("sts", region_name="us-east-1")
            account_info = sts_client.get_caller_identity()
            account_id = account_info["Account"]
            print(
                f"Retrieving       from account {account_id} using profile '{profile_name}'"
            )
        except ClientError:
            print(f"Retrieving website_secrets using profile '{profile_name}'")

        # Get the secret
        response = client.get_secret_value(SecretId="website_secrets")
        secret_string = response["SecretString"]

        # Parse the JSON secret
        try:
            return json.loads(secret_string)
        except json.JSONDecodeError as e:
            print(f"Error parsing secret JSON from profile '{profile_name}': {e}")
            return None

    except ProfileNotFound:
        print(f"AWS profile '{profile_name}' not found.")
        print("Available profiles can be listed with: aws configure list-profiles")
        return None

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceNotFoundException":
            print(f"Secret 'website_secrets' not found using profile '{profile_name}'")
        elif error_code == "AccessDeniedException":
            print(
                f"Access denied when trying to retrieve secret using profile '{profile_name}'"
            )
            print("Make sure the profile has proper permissions for SecretsManager")
        else:
            print(f"AWS error with profile '{profile_name}': {e}")
        return None

    except NoCredentialsError:
        print(f"No credentials found for profile '{profile_name}'.")
        print("Make sure the profile is properly configured in ~/.aws/credentials")
        return None

    except Exception as e:
        print(f"Unexpected error with profile '{profile_name}': {e}")
        return None


def update_secret_value(profile_name: str, secret_data: Dict[str, Any]) -> bool:
    """
    Update the website_secrets in the specified AWS profile.

    Args:
        profile_name: AWS profile name configured in ~/.aws/config or ~/.aws/credentials
        secret_data: Dictionary containing the updated secret data

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create session with the specified profile
        session = boto3.Session(profile_name=profile_name)
        client = session.client("secretsmanager", region_name="us-east-1")

        # Update the secret
        client.update_secret(
            SecretId="website_secrets", SecretString=json.dumps(secret_data)
        )
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
                f"Access denied when trying to update secret using profile '{profile_name}'"
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
        print(f"Unexpected error with profile '{profile_name}': {e}")
        return False


def copy_secret_property(
    source_profile: str,
    destination_profile: str,
    property_name: str,
    dry_run: bool = False,
) -> bool:
    """
    Copy a single property from website_secrets in source profile to destination profile.

    Args:
        source_profile: AWS profile name to copy from
        destination_profile: AWS profile name to copy to
        property_name: Name of the property within website_secrets to copy
        dry_run: If True, show what would be changed without making actual changes

    Returns:
        True if successful, False otherwise
    """
    action = "Previewing copy of" if dry_run else "Copying"
    print(
        f"{action} property '{property_name}' from profile '{source_profile}' to '{destination_profile}'"
    )

    # Get source secret
    print("Retrieving source secret...")
    source_secret = get_secret_value(source_profile)
    if not source_secret:
        print("Failed to retrieve source secret")
        return False

    if property_name not in source_secret:
        print(f"Property '{property_name}' not found in source secret")
        print(f"Available properties: {list(source_secret.keys())}")
        return False

    # Get destination secret
    print("Retrieving destination secret...")
    dest_secret = get_secret_value(destination_profile)
    if not dest_secret:
        print("Failed to retrieve destination secret")
        return False

    # Copy the property
    source_value = source_secret[property_name]

    # Show current vs new value
    if property_name in dest_secret:
        current_value = dest_secret[property_name]
        if current_value == source_value:
            print(
                f"Property '{property_name}' already has the same value in destination"
            )
        else:
            print(f"Property '{property_name}' current value: {current_value}")
            print(f"Property '{property_name}' new value: {source_value}")
    else:
        print(f"Property '{property_name}' will be added with value: {source_value}")

    # Create the updated secret
    updated_dest_secret = dest_secret.copy()
    updated_dest_secret[property_name] = source_value

    if dry_run:
        print("\n--- DRY RUN: Destination secret would be ---")
        print(json.dumps(updated_dest_secret, indent=2, sort_keys=True))
        print("--- End of dry run preview ---")
        print(
            f"Property '{property_name}' would be copied to destination profile (no changes made)"
        )
        return True
    else:
        # Update destination secret
        print(f"Updating destination secret with new value for '{property_name}'...")
        if update_secret_value(destination_profile, updated_dest_secret):
            print(
                f"Successfully copied property '{property_name}' to destination profile"
            )
            return True
        else:
            print("Failed to update destination secret")
            return False


def main():
    """Main function to parse arguments and execute the copy operation."""
    # Parse arguments
    args = sys.argv[1:]
    dry_run = False

    # Check for --dry-run flag
    if "--dry-run" in args:
        dry_run = True
        args.remove("--dry-run")

    # Check argument count
    if len(args) != 3:
        print(
            "Usage: python3 copy_website_secret.py <source_profile> <destination_profile> <property_name> [--dry-run]"
        )
        print(
            "Example: python3 copy_website_secret.py production sandbox DATABASE_PASSWORD"
        )
        print(
            "         python3 copy_website_secret.py sandbox production SECRET_KEY --dry-run"
        )
        print()
        print(
            "This script copies a single property from website_secrets in one AWS profile to another."
        )
        print("All other properties in the destination secret remain unchanged.")
        print()
        print("Options:")
        print(
            "  --dry-run    Show what the destination secret would look like without making changes"
        )
        print()
        print("Available profiles can be listed with: aws configure list-profiles")
        sys.exit(0)  # Exit without error when parameters are missing (as requested)

    source_profile = args[0]
    destination_profile = args[1]
    property_name = args[2]

    # Validate profile names (basic validation)
    if not source_profile.strip():
        print("Source profile name cannot be empty")
        sys.exit(0)

    if not destination_profile.strip():
        print("Destination profile name cannot be empty")
        sys.exit(0)

    if not property_name.strip():
        print("Property name cannot be empty")
        sys.exit(0)

    # Perform the copy operation
    success = copy_secret_property(
        source_profile, destination_profile, property_name, dry_run
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
