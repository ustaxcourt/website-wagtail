import os
import boto3
import string
import secrets
from botocore.exceptions import ClientError


def generate_random_password(length=16):
    """
    Generate a random password with letters, digits, and punctuation.
    Adjust as needed for your security or compliance requirements.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


def get_secret(secret_name):
    region_name = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name,
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
        print(f"{secret_name} retrieved from AWS Secrets Manager.")
        return response["SecretString"]

    except client.exceptions.ResourceNotFoundException:
        # The secret does not exist, so let's create it
        new_password = generate_random_password()
        try:
            client.create_secret(
                Name=secret_name,
                Description="Auto-generated secret for Wagtail user password.",
                SecretString=new_password,
            )
            print(f"Secret '{secret_name}' not found. Created a new secret.")
            return new_password
        except ClientError as e:
            raise RuntimeError(
                f"Failed to create secret '{secret_name}' in AWS Secrets Manager: {str(e)}"
            )
