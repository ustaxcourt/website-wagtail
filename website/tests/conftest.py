"""
Shared fixtures for testing snippet moderation workflow.
"""

import pytest
from django.contrib.auth.models import User, Group
from wagtail.models import Workflow
from wagtail.images.tests.utils import Image, get_test_image_file


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="testpass123",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def editor_user(db):
    """Create an editor user for testing."""
    editor_group, created = Group.objects.get_or_create(name="Editors")
    user = User.objects.create_user(
        username="editor",
        email="editor@example.com",
        password="testpass123",
        is_staff=True,
    )
    user.groups.add(editor_group)
    return user


@pytest.fixture
def moderator_user(db):
    """Create a moderator user for testing."""
    moderator_group, created = Group.objects.get_or_create(name="Moderators")
    user = User.objects.create_user(
        username="moderator",
        email="moderator@example.com",
        password="testpass123",
        is_staff=True,
    )
    user.groups.add(moderator_group)
    return user


@pytest.fixture
def regular_user(db):
    """Create a regular user for testing."""
    return User.objects.create_user(
        username="regular", email="regular@example.com", password="testpass123"
    )


@pytest.fixture
def test_workflow(db):
    """Create a basic workflow for testing."""
    workflow = Workflow.objects.create(name="Test Workflow")
    return workflow


@pytest.fixture
def test_image(db):
    """Create a test image for models that require images."""
    return Image.objects.create(
        title="Test image",
        file=get_test_image_file(),
    )
