import pytest
import string
from moto import mock_aws
import boto3
from botocore.exceptions import ClientError
import os
from home.utils.secrets import (
    generate_random_password,
    get_secret,
)  # Update import path as needed


def test_generate_random_password_default_length():
    """Test password generation with default length"""
    password = generate_random_password()
    assert len(password) == 16
    # Verify password contains at least one character from each required set
    assert any(c in string.ascii_letters for c in password)
    assert any(c in string.digits for c in password)
    assert any(c in string.punctuation for c in password)


def test_generate_random_password_custom_length():
    """Test password generation with custom length"""
    custom_length = 24
    password = generate_random_password(length=custom_length)
    assert len(password) == custom_length


def test_generate_random_password_uniqueness():
    """Test that generated passwords are unique"""
    passwords = [generate_random_password() for _ in range(5)]
    # Convert list to set to remove duplicates
    unique_passwords = set(passwords)
    assert len(passwords) == len(unique_passwords)


@mock_aws
def test_get_existing_secret():
    """Test retrieving an existing secret"""
    # Setup
    secret_name = "test-secret"
    secret_value = "my-test-secret-value"
    region_name = "us-east-1"

    # Create a mock secret
    client = boto3.client("secretsmanager", region_name=region_name)
    client.create_secret(Name=secret_name, SecretString=secret_value)

    # Test
    retrieved_secret = get_secret(secret_name)
    assert retrieved_secret == secret_value


@mock_aws
def test_get_nonexistent_secret():
    """Test retrieving a non-existent secret (should create new)"""
    secret_name = "nonexistent-secret"

    # Test
    retrieved_secret = get_secret(secret_name)

    # Verify
    assert retrieved_secret is not None
    assert len(retrieved_secret) == 16  # Default password length

    # Verify the secret was created in AWS
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    assert response["SecretString"] == retrieved_secret


@mock_aws
def test_get_secret_with_custom_region():
    """Test getting secret with custom AWS region"""
    # Setup
    secret_name = "test-secret"
    custom_region = "us-west-2"
    os.environ["AWS_DEFAULT_REGION"] = custom_region

    # Test
    retrieved_secret = get_secret(secret_name)

    # Cleanup
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"  # Reset to default

    assert retrieved_secret is not None


class MockSecretsManagerExceptions:
    class ResourceNotFoundException(ClientError):
        def __init__(self):
            super().__init__(
                error_response={
                    "Error": {
                        "Code": "ResourceNotFoundException",
                        "Message": "Secrets Manager can't find the specified secret.",
                    }
                },
                operation_name="GetSecretValue",
            )


class MockSecretsManagerClient:
    def __init__(self):
        self.exceptions = MockSecretsManagerExceptions

    def get_secret_value(self, SecretId):
        raise self.exceptions.ResourceNotFoundException()

    def create_secret(self, Name, Description, SecretString):
        raise ClientError(
            error_response={
                "Error": {
                    "Code": "InternalServiceError",
                    "Message": "Internal service error",
                }
            },
            operation_name="CreateSecret",
        )


@mock_aws
def test_create_secret_error(monkeypatch):
    """Test handling of secret creation error"""
    # Setup
    secret_name = "test-secret"

    def mock_client(*args, **kwargs):
        return MockSecretsManagerClient()

    # Patch the boto3 client creation
    monkeypatch.setattr(boto3.session.Session, "client", mock_client)

    # Test
    with pytest.raises(RuntimeError) as exc_info:
        get_secret(secret_name)

    assert "Failed to create secret" in str(exc_info.value)
    assert "Internal service error" in str(exc_info.value)


# Optional: Add fixtures if needed
@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def secretsmanager_client(aws_credentials):
    with mock_aws():
        yield boto3.client("secretsmanager", region_name="us-east-1")
