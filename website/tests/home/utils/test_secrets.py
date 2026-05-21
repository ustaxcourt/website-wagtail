import pytest
import string
import json
import os
from unittest.mock import patch, mock_open
from moto import mock_aws
import boto3
from botocore.exceptions import ClientError
from django.test import override_settings
from home.utils.secrets import (
    generate_random_password,
    get_secret,
    environment_is_local,
    read_local_secrets,
    write_local_secrets,
    get_secret_from_local,
)


class TestEnvironmentIsLocal:
    @override_settings(ENVIRONMENT="local")
    def test_returns_true_when_local(self):
        assert environment_is_local() is True

    @override_settings(ENVIRONMENT="production")
    def test_returns_false_when_not_local(self):
        assert environment_is_local() is False


class TestReadLocalSecrets:
    @override_settings(BASE_DIR="/tmp")
    def test_returns_empty_dict_when_file_not_found(self):
        with patch("os.path.isfile", return_value=False):
            assert read_local_secrets() == {}

    @override_settings(BASE_DIR="/tmp")
    def test_returns_dict_when_file_found(self):
        data = {"key": "value"}
        with patch("os.path.isfile", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(data))):
                assert read_local_secrets() == data

    @override_settings(BASE_DIR="/tmp")
    def test_raises_runtime_error_on_invalid_json(self):
        with patch("os.path.isfile", return_value=True):
            with patch("builtins.open", mock_open(read_data="not-json")):
                with pytest.raises(RuntimeError):
                    read_local_secrets()


class TestWriteLocalSecrets:
    def test_writes_json_to_file(self):
        data = {"key": "value"}
        m = mock_open()
        with patch("builtins.open", m):
            write_local_secrets(data, "test_file")
        m.assert_called_once_with("test_file", "w")


class TestGetSecretFromLocal:
    @override_settings(BASE_DIR="/tmp")
    def test_returns_existing_secret(self):
        with patch(
            "home.utils.secrets.read_local_secrets", return_value={"my_key": "my_val"}
        ):
            assert get_secret_from_local("my_key") == "my_val"

    @override_settings(BASE_DIR="/tmp")
    def test_creates_new_secret_when_missing(self):
        with patch("home.utils.secrets.read_local_secrets", return_value={}):
            with patch("home.utils.secrets.write_local_secrets") as mock_write:
                with patch(
                    "home.utils.secrets.generate_random_password",
                    return_value="new-pwd",
                ):
                    result = get_secret_from_local("new_key")
                    assert result == "new-pwd"
                    mock_write.assert_called_once()


class TestGetSecretRouting:
    @override_settings(ENVIRONMENT="local")
    def test_calls_local_when_environment_is_local(self):
        with patch(
            "home.utils.secrets.get_secret_from_local", return_value="local-val"
        ) as m:
            assert get_secret("my_secret") == "local-val"
            m.assert_called_once_with("my_secret")

    @override_settings(ENVIRONMENT="production")
    def test_calls_aws_when_not_local(self):
        with patch(
            "home.utils.secrets.get_secret_from_aws", return_value="aws-val"
        ) as m:
            assert get_secret("my_secret") == "aws-val"
            m.assert_called_once_with("my_secret")


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
