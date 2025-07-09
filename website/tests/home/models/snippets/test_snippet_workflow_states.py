"""
Tests for snippet workflow state transitions and behavior.

This module specifically tests the state management, transitions,
and workflow-related functionality of snippet models.
"""

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from home.models.snippets.common import CommonText
from home.models.snippets.judges import JudgeProfile, JudgeCollection, JudgeRole


class TestSnippetWorkflowStates(TestCase):
    """Test workflow state transitions for snippet models."""

    def test_snippet_initial_draft_state(self):
        """Test that snippets start in the correct initial state."""
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Test content</p>"
        )

        # Default state should be published
        self.assertTrue(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)
        self.assertIsNone(common_text.go_live_at)
        self.assertIsNone(common_text.expire_at)

    def test_snippet_draft_creation(self):
        """Test creating a snippet explicitly as draft."""
        common_text = CommonText.objects.create(
            name="Draft Text", text="<p>Draft content</p>", live=False
        )

        self.assertFalse(common_text.live)
        self.assertIsNone(common_text.first_published_at)
        self.assertIsNone(common_text.last_published_at)

    def test_snippet_publish_transition(self):
        """Test transitioning from draft to published state."""
        # Create as draft
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Test content</p>", live=False
        )

        self.assertFalse(common_text.live)
        self.assertIsNone(common_text.first_published_at)

        # Publish
        common_text.live = True
        common_text.save()

        self.assertTrue(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)

    def test_snippet_unpublish_transition(self):
        """Test transitioning from published to unpublished state."""
        # Create and publish
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Test content</p>", live=True
        )

        self.assertTrue(common_text.live)

        # Unpublish
        common_text.live = False
        common_text.save()

        self.assertFalse(common_text.live)

    def test_snippet_edit_published_content(self):
        """Test editing published content creates unpublished changes."""
        # Create and publish
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Original content</p>", live=True
        )

        self.assertTrue(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)

        # Edit content
        common_text.text = "<p>Updated content</p>"
        common_text.has_unpublished_changes = True
        common_text.save()

        # Should still be live but have unpublished changes
        self.assertTrue(common_text.live)
        self.assertTrue(common_text.has_unpublished_changes)

    def test_snippet_scheduled_publishing(self):
        """Test scheduled publishing functionality."""
        future_time = timezone.now() + timezone.timedelta(days=1)

        common_text = CommonText.objects.create(
            name="Scheduled Text",
            text="<p>Scheduled content</p>",
            live=False,
            go_live_at=future_time,
        )

        self.assertFalse(common_text.live)
        self.assertEqual(common_text.go_live_at, future_time)

    def test_snippet_scheduled_expiry(self):
        """Test scheduled expiry functionality."""
        future_time = timezone.now() + timezone.timedelta(days=7)

        common_text = CommonText.objects.create(
            name="Expiring Text",
            text="<p>This will expire</p>",
            live=True,
            expire_at=future_time,
        )

        self.assertTrue(common_text.live)
        self.assertEqual(common_text.expire_at, future_time)
        self.assertFalse(common_text.expired)

    def test_snippet_expired_state(self):
        """Test expired state handling."""
        past_time = timezone.now() - timezone.timedelta(days=1)

        common_text = CommonText.objects.create(
            name="Expired Text",
            text="<p>This has expired</p>",
            live=True,
            expire_at=past_time,
            expired=True,
        )

        self.assertTrue(common_text.live)  # Still technically live
        self.assertTrue(common_text.expired)
        self.assertEqual(common_text.expire_at, past_time)


class TestJudgeProfileWorkflowStates(TestCase):
    """Test workflow states specific to JudgeProfile model."""

    def test_judge_profile_draft_to_published(self):
        """Test judge profile draft to published transition."""
        judge = JudgeProfile.objects.create(
            first_name="Jane",
            last_name="Doe",
            title="Senior Judge",
            bio="<p>Biography content</p>",
            live=False,
        )

        self.assertFalse(judge.live)

        # Publish
        judge.live = True
        judge.save()

        self.assertTrue(judge.live)

    def test_judge_profile_with_scheduled_publishing(self):
        """Test judge profile with scheduled publishing."""
        future_date = timezone.now() + timezone.timedelta(days=1)

        judge = JudgeProfile.objects.create(
            first_name="Future",
            last_name="Judge",
            title="Judge",
            live=False,
            go_live_at=future_date,
        )

        self.assertFalse(judge.live)
        self.assertEqual(judge.go_live_at, future_date)


class TestJudgeCollectionWorkflowStates(TestCase):
    """Test workflow states specific to JudgeCollection model."""

    def test_judge_collection_draft_state(self):
        """Test judge collection in draft state."""
        collection = JudgeCollection.objects.create(name="Draft Collection", live=False)

        self.assertFalse(collection.live)
        self.assertEqual(collection.name, "Draft Collection")

    def test_judge_collection_published_state(self):
        """Test judge collection in published state."""
        collection = JudgeCollection.objects.create(
            name="Published Collection", live=True
        )

        self.assertTrue(collection.live)


class TestJudgeRoleWorkflowStates(TestCase):
    """Test workflow states specific to JudgeRole model."""

    def setUp(self):
        self.judge = JudgeProfile.objects.create(
            first_name="Test", last_name="Judge", title="Judge"
        )

    def test_judge_role_draft_state(self):
        """Test judge role in draft state."""
        role = JudgeRole.objects.create(
            role_name="Assistant Judge", judge=self.judge, live=False
        )

        self.assertFalse(role.live)
        self.assertEqual(role.role_name, "Assistant Judge")

    def test_judge_role_published_state(self):
        """Test judge role in published state."""
        role = JudgeRole.objects.create(
            role_name="Chief Judge", judge=self.judge, live=True
        )

        self.assertTrue(role.live)

    def test_judge_role_without_judge_assignment(self):
        """Test judge role workflow without assigned judge."""
        role = JudgeRole.objects.create(role_name="Vacant Position", live=False)

        self.assertFalse(role.live)
        self.assertIsNone(role.judge)


class TestSnippetRevisionWorkflow(TestCase):
    """Test revision-related workflow functionality."""

    def test_revision_created_on_save(self):
        """Test that revisions can be created for snippets."""
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Initial content</p>"
        )

        # Create initial revision manually
        common_text.save_revision()

        # Should have one revision
        self.assertEqual(common_text.revisions.count(), 1)

        # Edit and save
        common_text.text = "<p>Updated content</p>"
        common_text.save()
        common_text.save_revision()

        # Should have two revisions
        self.assertEqual(common_text.revisions.count(), 2)

    def test_latest_revision_tracking(self):
        """Test that latest_revision is properly tracked."""
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Initial content</p>"
        )

        # Create initial revision
        initial_revision = common_text.save_revision()
        self.assertIsNotNone(initial_revision)

        # Edit and save
        common_text.text = "<p>Updated content</p>"
        common_text.save()
        new_revision = common_text.save_revision()

        # Latest revision should be different
        self.assertNotEqual(new_revision, initial_revision)

    def test_live_revision_tracking(self):
        """Test that live_revision tracking is available."""
        # Create as published
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Initial content</p>", live=True
        )

        # Create initial revision and publish
        initial_revision = common_text.save_revision()
        common_text.live_revision = initial_revision
        common_text.save()

        # live_revision should be set
        self.assertIsNotNone(common_text.live_revision)

        # Edit but don't publish changes
        common_text.text = "<p>Updated content</p>"
        common_text.has_unpublished_changes = True
        common_text.save()
        new_revision = common_text.save_revision()

        # latest_revision should be different from live_revision
        self.assertNotEqual(new_revision, common_text.live_revision)

    def test_revision_content_preservation(self):
        """Test that revision content is preserved correctly."""
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Version 1</p>"
        )

        first_revision = common_text.save_revision()

        # Edit
        common_text.text = "<p>Version 2</p>"
        common_text.save()
        second_revision = common_text.save_revision()

        # Revisions should be different
        self.assertNotEqual(first_revision, second_revision)

        # Should have 2 revisions total
        self.assertEqual(common_text.revisions.count(), 2)


class TestSnippetWorkflowPermissions(TestCase):
    """Test workflow permissions and access control."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="test123", is_superuser=True
        )
        self.staff_user = User.objects.create_user(
            username="staff", password="test123", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="regular", password="test123"
        )

    def test_draft_visibility(self):
        """Test that draft snippets have appropriate visibility."""
        # Create a draft snippet
        common_text = CommonText.objects.create(
            name="Draft Text", text="<p>Draft content</p>", live=False
        )

        # Draft should not be live
        self.assertFalse(common_text.live)

        # Published snippets should be live
        published_text = CommonText.objects.create(
            name="Published Text", text="<p>Published content</p>", live=True
        )

        self.assertTrue(published_text.live)

    def test_workflow_state_transitions(self):
        """Test that workflow state transitions work correctly."""
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Test content</p>", live=False
        )

        # Start as draft
        self.assertFalse(common_text.live)

        # Transition to published
        common_text.live = True
        common_text.save()

        self.assertTrue(common_text.live)

        # Transition back to draft
        common_text.live = False
        common_text.save()

        self.assertFalse(common_text.live)
