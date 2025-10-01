#!/usr/bin/env python3
"""
Script to retrieve a specific property from website_secrets in an AWS account,
or display the entire secret if no property is specified.

Usage:
    python3 get_website_secret.py <profile_name> [<property_name>]

Example:
    python3 get_website_secret.py sandbox DATABASE_PASSWORD
    python3 get_website_secret.py production SECRET_KEY
    python3 get_website_secret.py default DOMAIN_NAME
    python3 get_website_secret.py sandbox    # Shows entire secret

Requirements:
    pip install boto3
"""

import json
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from typing import Optional, Dict, Any


def get_website_secret_property(
    profile_name: str, property_name: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Retrieve website_secrets or a specific property from it using the specified AWS profile.

    Args:
        profile_name: AWS profile name configured in ~/.aws/config or ~/.aws/credentials
        property_name: Optional name of the property within website_secrets to retrieve.
                      If None, returns the entire secret data.

    Returns:
        Dictionary containing the secret data or property value if found, None otherwise
    """
    try:
        # Create a session with the specified profile
        session = boto3.Session(profile_name=profile_name)
        client = session.client("secretsmanager", region_name="us-east-1")

        # Get the secret
        response = client.get_secret_value(SecretId="website_secrets")
        secret_string = response["SecretString"]

        # Parse the JSON secret
        try:
            secret_data = json.loads(secret_string)
        except json.JSONDecodeError as e:
            print(f"Error parsing secret JSON: {e}", file=sys.stderr)
            return None

        # Return entire secret if no property name specified
        if property_name is None:
            return secret_data

        # Check if the specific property exists
        if property_name not in secret_data:
            print(
                f"Property '{property_name}' not found in website_secrets",
                file=sys.stderr,
            )
            print(f"Available properties: {list(secret_data.keys())}", file=sys.stderr)
            return None

        # Return just the property value wrapped in a dict for consistency
        return {property_name: secret_data[property_name]}

    except ProfileNotFound:
        print(f"AWS profile '{profile_name}' not found.", file=sys.stderr)
        print(
            "Available profiles can be listed with: aws configure list-profiles",
            file=sys.stderr,
        )
        print(
            "Or check your ~/.aws/config and ~/.aws/credentials files", file=sys.stderr
        )
        return None

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceNotFoundException":
            print(
                f"Secret 'website_secrets' not found using profile '{profile_name}'",
                file=sys.stderr,
            )
        elif error_code == "AccessDeniedException":
            print(
                f"Access denied when trying to retrieve secret using profile '{profile_name}'",
                file=sys.stderr,
            )
            print(
                "Make sure the profile has proper permissions for SecretsManager",
                file=sys.stderr,
            )
        else:
            print(f"AWS error: {e}", file=sys.stderr)
        return None

    except NoCredentialsError:
        print(f"No credentials found for profile '{profile_name}'.", file=sys.stderr)
        print(
            "Make sure the profile is properly configured in ~/.aws/credentials",
            file=sys.stderr,
        )
        return None

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return None


def main():
    """Main function to parse arguments and retrieve the secret property or entire secret."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(
            "Usage: python3 get_website_secret.py <profile_name> [<property_name>]",
            file=sys.stderr,
        )
        print(
            "Example: python3 get_website_secret.py sandbox DATABASE_PASSWORD",
            file=sys.stderr,
        )
        print(
            "         python3 get_website_secret.py production SECRET_KEY",
            file=sys.stderr,
        )
        print(
            "         python3 get_website_secret.py default DOMAIN_NAME",
            file=sys.stderr,
        )
        print(
            "         python3 get_website_secret.py sandbox    # Shows entire secret",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print(
            "This script retrieves a specific property or the entire 'website_secrets' secret",
            file=sys.stderr,
        )
        print(
            "in AWS Secrets Manager using the specified AWS profile.", file=sys.stderr
        )
        print("", file=sys.stderr)
        print(
            "Available profiles can be listed with: aws configure list-profiles",
            file=sys.stderr,
        )
        sys.exit(0)  # Exit without error when parameters are missing

    profile_name = sys.argv[1]
    property_name = sys.argv[2] if len(sys.argv) == 3 else None

    # Validate profile name (basic validation)
    if not profile_name.strip():
        print("Profile name cannot be empty", file=sys.stderr)
        sys.exit(0)

    if property_name is not None and not property_name.strip():
        print("Property name cannot be empty", file=sys.stderr)
        sys.exit(0)

    # Retrieve the property or entire secret
    result = get_website_secret_property(profile_name, property_name)

    if result is not None:
        if property_name is None:
            # Output entire secret as JSON
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            # Output just the property value
            print(result[property_name])
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
