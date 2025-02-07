import os
import json
import boto3
import string
import secrets
from botocore.exceptions import ClientError
from django.conf import settings


def environment_is_local():
    try:
        return settings.ENVIRONMENT == "local"
    except (AttributeError, KeyError):
        return False


def read_local_secrets(filename="website_secrets"):
    file_with_path = os.path.join(settings.BASE_DIR, filename)
    if not os.path.isfile(file_with_path):
        return {}
    try:
        with open(file_with_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Could not parse JSON, or some file error occurred
        print(f"Error reading or parsing '{file_with_path}'.")
        raise RuntimeError(f"Error reading or parsing '{file_with_path}'.")


def write_local_secrets(data, filename="website_secrets"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def generate_random_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


def get_secret_from_aws(secret_name):
    region_name = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    secret_id = "website_secrets"

    session = boto3.session.Session()
    # Correct service_name to 'secretsmanager'
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name,
    )

    try:
        # Try to fetch the existing 'website_secrets'
        response = client.get_secret_value(SecretId=secret_id)
        secret_str = response["SecretString"]
        secret_dict = json.loads(secret_str)  # parse JSON into a dict

        # If `secret_name` exists, return it
        if secret_name in secret_dict:
            print(f"'{secret_name}' retrieved from AWS Secrets Manager.")
            return secret_dict[secret_name]
        else:
            # `secret_name` does not exist, so let's create it
            print(f"'{secret_name}' not found in '{secret_id}'. Generating new value.")
            secret_dict[secret_name] = generate_random_password()
            client.put_secret_value(
                SecretId=secret_id,
                SecretString=json.dumps(secret_dict),
            )
            print(f"Updated '{secret_id}' with key '{secret_name}'.")
            return secret_dict[secret_name]

    except client.exceptions.ResourceNotFoundException:
        # 'website_secrets' does not exist at all, so let's create it
        print(f"'{secret_id}' not found in AWS Secrets Manager. Creating a new secret.")
        new_password = generate_random_password()
        secret_dict = {secret_name: new_password}

        try:
            client.create_secret(
                Name=secret_id,
                Description="Auto-generated JSON secret for 'website_secrets'.",
                SecretString=json.dumps(secret_dict),
            )
            print(f"Created '{secret_id}' with key '{secret_name}'.")
            return new_password
        except ClientError as e:
            raise RuntimeError(
                f"Failed to create secret '{secret_id}' in AWS Secrets Manager: {str(e)}"
            ) from e

    except ClientError as e:
        # Other AWS-related errors
        raise RuntimeError(
            f"Failed to retrieve or update '{secret_id}' in AWS Secrets Manager: {str(e)}"
        ) from e


def get_secret_from_local(secret_name, filename="website_secrets"):
    data = read_local_secrets(filename)

    if secret_name in data:
        print(f"'{secret_name}' retrieved from local secrets file '{filename}'.")
        return data[secret_name]
    else:
        # `secret_name` does not exist locally; create a new one
        new_password = generate_random_password()
        data[secret_name] = new_password
        write_local_secrets(data, filename)
        print(
            f"Secret '{secret_name}' not found in '{filename}'; created new secret locally."
        )
        return new_password


def get_secret(secret_name):
    if environment_is_local():
        return get_secret_from_local(secret_name)
    else:
        return get_secret_from_aws(secret_name)
