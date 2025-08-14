import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime

from home.models.utils.execute_script import ExecuteScript


User = get_user_model()


@pytest.fixture
def mock_user():
    """Create a real user for testing."""
    return User.objects.create_user(
        username="testuser", email="test@example.com", is_superuser=True
    )


@pytest.fixture
def mock_datetime():
    """Create a mock datetime for consistent testing."""
    return timezone.make_aware(datetime(2024, 1, 15, 10, 30, 0))


class TestExecuteScriptCommandExists:
    """Test cases for the command_exists class method."""

    @pytest.mark.django_db
    def test_command_exists_true_with_default_execution_type(self):
        """Test that command_exists returns True when script exists with ONETIME type."""
        ExecuteScript.objects.create(
            command_name="test_command",
            execution_type="ONETIME",
            execution_status="PENDING",
        )

        assert ExecuteScript.command_exists("test_command") is True

    @pytest.mark.django_db
    def test_command_exists_false_when_script_not_found(self):
        """Test that command_exists returns False when script doesn't exist."""
        assert ExecuteScript.command_exists("nonexistent_command") is False

    @pytest.mark.django_db
    def test_command_exists_with_specific_execution_type(self):
        """Test command_exists with specific execution type."""
        ExecuteScript.objects.create(
            command_name="test_command",
            execution_type="EVERYTIME",
            execution_status="PENDING",
        )

        assert (
            ExecuteScript.command_exists("test_command", execution_type="EVERYTIME")
            is True
        )
        assert (
            ExecuteScript.command_exists("test_command", execution_type="ONETIME")
            is False
        )

    @pytest.mark.django_db
    def test_command_exists_with_none_execution_type(self):
        """Test command_exists with None execution type checks any type."""
        ExecuteScript.objects.create(
            command_name="test_command",
            execution_type="EVERYTIME",
            execution_status="PENDING",
        )

        assert ExecuteScript.command_exists("test_command", execution_type=None) is True

    def test_command_exists_invalid_execution_type_raises_error(self):
        """Test that invalid execution_type raises ValueError."""
        with pytest.raises(ValueError, match="execution_type must be one of"):
            ExecuteScript.command_exists("test_command", execution_type="INVALID")

    @pytest.mark.django_db
    def test_command_exists_case_sensitive(self):
        """Test that command name matching is case sensitive."""
        ExecuteScript.objects.create(
            command_name="Test_Command",
            execution_type="ONETIME",
            execution_status="PENDING",
        )

        assert ExecuteScript.command_exists("Test_Command") is True
        assert ExecuteScript.command_exists("test_command") is False


class TestExecuteScriptCreateScript:
    """Test cases for the create_script class method."""

    @pytest.mark.django_db
    @patch("home.models.utils.execute_script.timezone.now")
    def test_create_script_with_defaults(self, mock_now, mock_user, mock_datetime):
        """Test create_script with all default values."""
        mock_now.return_value = mock_datetime

        script = ExecuteScript.create_script("test_command")

        assert script.command_name == "test_command"
        assert script.execution_type == "ONETIME"
        assert script.execution_status == "PENDING"
        assert script.datetime == mock_datetime
        assert script.created_by == mock_user
        assert script.updated_by == mock_user

    @pytest.mark.django_db
    def test_create_script_with_custom_values(self, mock_datetime):
        """Test create_script with custom values."""
        custom_user = User.objects.create_user(
            username="customuser", email="custom@example.com"
        )

        script = ExecuteScript.create_script(
            command_name="custom_command",
            execution_type="EVERYTIME",
            execution_status="SUCCESS",
            datetime=mock_datetime,
            created_by=custom_user,
            updated_by=custom_user,
        )

        assert script.command_name == "custom_command"
        assert script.execution_type == "EVERYTIME"
        assert script.execution_status == "SUCCESS"
        assert script.datetime == mock_datetime
        assert script.created_by == custom_user
        assert script.updated_by == custom_user

    def test_create_script_invalid_execution_type_raises_error(self):
        """Test that invalid execution_type raises ValueError."""
        with pytest.raises(ValueError, match="execution_type must be one of"):
            ExecuteScript.create_script("test_command", execution_type="INVALID")

    def test_create_script_invalid_execution_status_raises_error(self):
        """Test that invalid execution_status raises ValueError."""
        with pytest.raises(ValueError, match="execution_status must be one of"):
            ExecuteScript.create_script("test_command", execution_status="INVALID")

    @pytest.mark.django_db
    @patch("home.models.utils.execute_script.timezone.now")
    def test_create_script_no_superuser_available(self, mock_now, mock_datetime):
        """Test create_script when no superuser is available."""
        mock_now.return_value = mock_datetime
        # Don't create any superusers, so the default should be None

        script = ExecuteScript.create_script("test_command")

        assert script.command_name == "test_command"
        assert script.created_by is None
        assert script.updated_by is None

    @pytest.mark.django_db
    def test_create_script_partial_user_defaults(self, mock_user):
        """Test create_script with partial user specification."""
        custom_user = User.objects.create_user(
            username="customuser2", email="custom2@example.com"
        )

        script = ExecuteScript.create_script("test_command", created_by=custom_user)

        assert script.created_by == custom_user
        assert script.updated_by == mock_user


class TestExecuteScriptIntegration:
    """Integration tests for ExecuteScript methods working together."""

    @pytest.mark.django_db
    def test_create_then_check_exists(self, mock_user):
        """Test creating a script and then checking if it exists."""
        command_name = "integration_test_command"

        # Initially should not exist
        assert ExecuteScript.command_exists(command_name) is False

        # Create the script
        ExecuteScript.create_script(command_name)

        # Now should exist
        assert ExecuteScript.command_exists(command_name) is True

    @pytest.mark.django_db
    def test_create_duplicate_prevention_pattern(self, mock_user):
        """Test the common pattern of checking existence before creation."""
        command_name = "duplicate_test_command"

        # First creation should succeed
        if not ExecuteScript.command_exists(command_name):
            script1 = ExecuteScript.create_script(command_name)
            assert script1 is not None

        # Second attempt should skip creation
        if not ExecuteScript.command_exists(command_name):
            script2 = ExecuteScript.create_script(command_name)
        else:
            script2 = None

        assert script2 is None
        assert ExecuteScript.objects.filter(command_name=command_name).count() == 1

    @pytest.mark.django_db
    def test_model_str_representation(self):
        """Test the string representation of ExecuteScript model."""
        script = ExecuteScript.objects.create(
            command_name="test_str_command",
            execution_type="ONETIME",
            execution_status="PENDING",
        )

        assert str(script) == "test_str_command"

    @pytest.mark.django_db
    def test_model_ordering(self):
        """Test that ExecuteScript models are ordered by created_at descending."""
        # Create scripts with slight delay to ensure different created_at times
        script1 = ExecuteScript.objects.create(
            command_name="first_command",
            execution_type="ONETIME",
            execution_status="PENDING",
        )

        script2 = ExecuteScript.objects.create(
            command_name="second_command",
            execution_type="ONETIME",
            execution_status="PENDING",
        )

        # Get all scripts ordered by model's Meta ordering
        scripts = list(ExecuteScript.objects.all())

        # Most recent should be first
        assert scripts[0] == script2
        assert scripts[1] == script1


class TestExecuteScriptEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.django_db
    def test_command_name_with_special_characters(self):
        """Test command names with special characters."""
        special_names = [
            "command-with-dashes",
            "command_with_underscores",
            "command with spaces",
            "command@with#symbols",
            "命令-with-unicode",
        ]

        for name in special_names:
            script = ExecuteScript.objects.create(
                command_name=name, execution_type="ONETIME", execution_status="PENDING"
            )
            assert ExecuteScript.command_exists(name) is True
            assert str(script) == name

    @pytest.mark.django_db
    def test_very_long_command_name(self):
        """Test handling of very long command names."""
        long_name = "a" * 255  # Max length according to model

        script = ExecuteScript.objects.create(
            command_name=long_name, execution_type="ONETIME", execution_status="PENDING"
        )

        assert ExecuteScript.command_exists(long_name) is True
        assert script.command_name == long_name

    def test_execution_type_choices_validation(self):
        """Test that EXECUTION_TYPE_CHOICES contains expected values."""
        choices = [choice[0] for choice in ExecuteScript.EXECUTION_TYPE_CHOICES]
        assert "ONETIME" in choices
        assert "EVERYTIME" in choices
        assert len(choices) == 2

    def test_execution_status_choices_validation(self):
        """Test that EXECUTION_STATUS_CHOICES contains expected values."""
        choices = [choice[0] for choice in ExecuteScript.EXECUTION_STATUS_CHOICES]
        assert "SUCCESS" in choices
        assert "FAILURE" in choices
        assert "PENDING" in choices
        assert len(choices) == 3
