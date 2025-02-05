import os
import boto3
import string
import secrets
import json
from botocore.exceptions import ClientError
from django.conf import settings


def environment_is_local():
    try:
        return True if settings.ENVIRONMENT == "local" else False
    except KeyError:
        return False


def read_local_secrets(filename="website_secrets"):
    """
    Read JSON data from a local secrets file.
    If the file does not exist or is invalid, return an empty dict.
    """
    if not os.path.isfile(filename):
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Could not parse JSON, or an OS error occurred
        return {}


def write_local_secrets(data, filename="website_secrets"):
    """
    Write JSON data to the local secrets file.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def generate_random_password(length=16):
    """
    Generate a random password with letters, digits, and punctuation.
    Adjust as needed for your security or compliance requirements.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


def get_secret_from_aws(secret_name):
    region_name = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    secret_id = "website_secrets"

    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name,
    )

    secret_dict = {}
    try:
        response = client.get_secret_value(SecretId="website_secrets")
        secret_dict = json.loads(response["SecretString"])

        if secret_name in secret_dict:
            print(f"'{secret_name}' retrieved from AWS Secrets Manager.")
            return secret_dict[secret_name]
        else:
            print(f"{secret_name} is not in the response from AWS Secrets Manager.")
            secret_dict[secret_name] = generate_random_password()
            client.put_secret_value(
                SecretId=secret_id, SecretString=json.dumps(secret_dict)
            )
            return response[secret_name]

    except client.exceptions.ResourceNotFoundException:
        # The secret does not exist, so let's create it
        new_password = generate_random_password()
        secret_dict[secret_name] = new_password
        try:
            client.create_secret(
                Name=secret_id,
                Description="Auto-generated secret for Wagtail user password.",
                SecretString=json.dumps(response),
            )
            print(f"Secret '{secret_name}' not found. Created a new secret.")
            return new_password
        except ClientError as e:
            raise RuntimeError(
                f"Failed to create secret '{secret_name}' in AWS Secrets Manager: {str(e)}"
            )


def get_secret_from_local(secret_name, filename="website_secrets"):
    """
    Retrieve a secret from a local JSON file; create it if it doesn't exist.
    """
    data = read_local_secrets(filename)

    if secret_name in data:
        print(f"{secret_name} retrieved from local secrets file '{filename}'.")
        return data[secret_name]
    else:
        # Secret does not exist locally; create a new one
        new_password = generate_random_password()
        data[secret_name] = new_password
        write_local_secrets(data, filename)
        print(
            f"Secret '{secret_name}' not found in '{filename}'; created new secret locally."
        )
        return new_password


def get_secret(secret_name):
    """
    Retrieve or create a secret.
    - If in AWS environment, use AWS Secrets Manager.
    - Otherwise, use local 'website_secrets' JSON file.
    """
    return (
        get_secret_from_local(secret_name)
        if environment_is_local()
        else get_secret_from_aws(secret_name)
    )
