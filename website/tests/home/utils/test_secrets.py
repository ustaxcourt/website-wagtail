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
import json


def test_generate_random_password_default_length():
    """Test password generation with default length"""
    password = generate_random_password()
    assert len(password) == 16
    # Verify password contains at least one ASCII letter
    assert any(c in string.ascii_letters for c in password)


def test_generate_random_password_custom_length():
    """Test password generation with custom length"""
    custom_length = 24
    password = generate_random_password(length=custom_length)
    assert len(password) == custom_length


def test_generate_random_password_uniqueness():
    """Test that generated passwords are unique"""
    passwords = [generate_random_password() for _ in range(5)]
    unique_passwords = set(passwords)
    assert len(passwords) == len(unique_passwords)


@pytest.fixture
def aws_credentials():
    """
    Mocked AWS Credentials for moto.
    Ensures no real AWS connection is made.
    """
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def secretsmanager_client(aws_credentials):
    """
    A fixture that mocks AWS using moto's @mock_aws decorator.
    This yields a Secrets Manager client for tests.
    """
    with mock_aws():
        yield boto3.client("secretsmanager", region_name="us-east-1")


@pytest.mark.usefixtures("secretsmanager_client")
def test_get_existing_secret():
    """
    Test retrieving an existing key from 'website_secrets' in AWS Secrets Manager.
    """
    # Setup
    website_secret_name = "website_secrets"
    test_key = "test-secret"
    test_value = "my-test-secret-value"

    # Create a mock 'website_secrets' with JSON that has {'test-secret': 'my-test-secret-value'}
    client = boto3.client("secretsmanager", region_name="us-east-1")
    secret_data = {test_key: test_value}
    client.create_secret(
        Name=website_secret_name,
        SecretString=json.dumps(secret_data),
    )

    # Act
    retrieved_secret = get_secret(test_key)  # calls get_secret_from_aws internally
    # Assert
    assert retrieved_secret == test_value


@pytest.mark.usefixtures("secretsmanager_client")
def test_get_nonexistent_secret():
    """
    Test retrieving a key that doesn't exist in 'website_secrets'.
    The code should create it and store a newly generated password.
    """
    website_secret_name = "website_secrets"
    test_key = "nonexistent-secret"

    # Create a mock 'website_secrets' but leave it empty
    client = boto3.client("secretsmanager", region_name="us-east-1")
    client.create_secret(
        Name=website_secret_name,
        SecretString=json.dumps({}),  # empty JSON
    )

    # Act
    retrieved_secret = get_secret(test_key)

    # Verify the newly generated secret is not None and has length 16
    assert retrieved_secret is not None
    assert len(retrieved_secret) == 16

    # The secret was updated in AWS. Let's confirm.
    response = client.get_secret_value(SecretId=website_secret_name)
    secret_data = json.loads(response["SecretString"])
    assert secret_data[test_key] == retrieved_secret


@pytest.mark.usefixtures("secretsmanager_client")
def test_get_secret_with_custom_region():
    """
    Test retrieving a key (which triggers secret creation) in a custom region.
    """
    custom_region = "us-west-2"
    os.environ["AWS_DEFAULT_REGION"] = custom_region

    test_key = "custom-region-secret"
    # We haven't created 'website_secrets' explicitly, so the code will create it.
    retrieved_secret = get_secret(test_key)

    # Cleanup - reset region
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    assert retrieved_secret is not None
    assert len(retrieved_secret) == 16


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
    """
    A mock client to simulate ResourceNotFoundException and then fail on create_secret.
    """

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


@pytest.mark.usefixtures("aws_credentials")
def test_create_secret_error(monkeypatch):
    """
    Test handling of secret creation error in AWS Secrets Manager.
    """
    test_key = "test-secret"

    def mock_client(*args, **kwargs):
        return MockSecretsManagerClient()

    # Patch the boto3 client creation to return our mock
    monkeypatch.setattr(boto3.session.Session, "client", mock_client)

    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        get_secret(test_key)

    assert "Failed to create secret" in str(exc_info.value)
    assert "Internal service error" in str(exc_info.value)
