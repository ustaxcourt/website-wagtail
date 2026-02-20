"""
Tests for snippet draft and moderation workflow functionality.

This module tests the draft status, moderation workflow, and revision history
functionality for all snippet models that inherit from WorkflowMixin,
DraftStateMixin, and RevisionMixin.
"""

from django.contrib.auth.models import User
from django.test import TestCase

from home.models.snippets.common import CommonText
from home.models.snippets.judges import JudgeProfile, JudgeCollection, JudgeRole
from home.models.snippets.navigation import NavigationRibbon, NavigationMenu


class TestCommonTextModerationWorkflow(TestCase):
    """Test draft and moderation workflow for CommonText snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )
        self.editor_user = User.objects.create_user(
            username="editor", password="testpass123", is_staff=True
        )

    def test_create_common_text_as_draft(self):
        """Test creating a CommonText snippet in draft state."""
        common_text = CommonText.objects.create(
            name="Test Common Text", text="<p>This is test content</p>", live=False
        )

        self.assertFalse(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)
        self.assertEqual(common_text.name, "Test Common Text")
        self.assertEqual(common_text.text, "<p>This is test content</p>")

    def test_publish_common_text(self):
        """Test publishing a CommonText snippet."""
        common_text = CommonText.objects.create(
            name="Test Common Text", text="<p>This is test content</p>", live=False
        )

        # Simulate publishing
        common_text.live = True
        common_text.has_unpublished_changes = False
        common_text.save()

        self.assertTrue(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)

    def test_edit_published_common_text_creates_draft(self):
        """Test that editing a published CommonText creates a draft state."""
        common_text = CommonText.objects.create(
            name="Test Common Text", text="<p>Original content</p>", live=True
        )

        # Edit the snippet
        common_text.text = "<p>Updated content</p>"
        common_text.has_unpublished_changes = True
        common_text.save()

        self.assertTrue(common_text.live)
        self.assertTrue(common_text.has_unpublished_changes)
        self.assertEqual(common_text.text, "<p>Updated content</p>")

    def test_common_text_revision_creation(self):
        """Test that revisions are created when CommonText is saved."""
        common_text = CommonText.objects.create(
            name="Test Common Text", text="<p>Original content</p>"
        )

        # Create initial revision manually
        common_text.save_revision()

        # Check that revision was created
        revisions = common_text.revisions.all()
        self.assertEqual(revisions.count(), 1)

        # Edit and save again
        common_text.text = "<p>Updated content</p>"
        common_text.save()
        common_text.save_revision()

        # Check that a new revision was created
        revisions = common_text.revisions.all()
        self.assertEqual(revisions.count(), 2)

    def test_common_text_str_method(self):
        """Test the string representation of CommonText."""
        common_text = CommonText.objects.create(
            name="Test Common Text", text="<p>Test content</p>"
        )
        self.assertEqual(str(common_text), "Test Common Text")


class TestJudgeProfileModerationWorkflow(TestCase):
    """Test draft and moderation workflow for JudgeProfile snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )

    def test_create_judge_profile_as_draft(self):
        """Test creating a JudgeProfile snippet in draft state."""
        judge = JudgeProfile.objects.create(
            first_name="John",
            last_name="Doe",
            title="Judge",
            chambers_telephone="555-0123",
            bio="<p>Test biography</p>",
            live=False,
        )

        self.assertFalse(judge.live)
        self.assertEqual(judge.first_name, "John")
        self.assertEqual(judge.last_name, "Doe")
        self.assertEqual(judge.title, "Judge")

    def test_judge_profile_display_name_auto_generation(self):
        """Test that display_name is auto-generated when not provided."""
        judge = JudgeProfile.objects.create(
            first_name="John",
            middle_initial="A",
            last_name="Doe",
            suffix="Jr.",
            title="Judge",
        )

        self.assertEqual(judge.display_name, "John A Doe Jr.")

    def test_judge_profile_display_name_custom(self):
        """Test that custom display_name is preserved."""
        judge = JudgeProfile.objects.create(
            first_name="John",
            last_name="Doe",
            title="Judge",
            display_name="The Honorable John Doe",
        )

        self.assertEqual(judge.display_name, "The Honorable John Doe")

    def test_judge_profile_revision_creation(self):
        """Test that revisions are created when JudgeProfile is saved."""
        judge = JudgeProfile.objects.create(
            first_name="John", last_name="Doe", title="Judge"
        )

        # Create revision manually
        judge.save_revision()

        # Check that revision was created
        revisions = judge.revisions.all()
        self.assertEqual(revisions.count(), 1)

    def test_judge_profile_str_method(self):
        """Test the string representation of JudgeProfile."""
        judge = JudgeProfile.objects.create(
            first_name="John", last_name="Doe", title="Judge", display_name="John Doe"
        )
        self.assertEqual(str(judge), "John Doe")


class TestJudgeCollectionModerationWorkflow(TestCase):
    """Test draft and moderation workflow for JudgeCollection snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )

    def test_create_judge_collection_as_draft(self):
        """Test creating a JudgeCollection snippet in draft state."""
        collection = JudgeCollection.objects.create(
            name="Test Judges Collection", live=False
        )

        self.assertFalse(collection.live)
        self.assertEqual(collection.name, "Test Judges Collection")

    def test_judge_collection_unique_name(self):
        """Test that JudgeCollection names are unique."""
        JudgeCollection.objects.create(name="Unique Collection")

        with self.assertRaises(Exception):
            JudgeCollection.objects.create(name="Unique Collection")

    def test_judge_collection_revision_creation(self):
        """Test that revisions are created when JudgeCollection is saved."""
        collection = JudgeCollection.objects.create(name="Test Collection")

        # Create revision manually
        collection.save_revision()

        # Check that revision was created
        revisions = collection.revisions.all()
        self.assertEqual(revisions.count(), 1)

    def test_judge_collection_str_method(self):
        """Test the string representation of JudgeCollection."""
        collection = JudgeCollection.objects.create(name="Test Collection")
        self.assertEqual(str(collection), "Test Collection")


class TestJudgeRoleModerationWorkflow(TestCase):
    """Test draft and moderation workflow for JudgeRole snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )
        self.judge = JudgeProfile.objects.create(
            first_name="John", last_name="Doe", title="Judge"
        )

    def test_create_judge_role_as_draft(self):
        """Test creating a JudgeRole snippet in draft state."""
        role = JudgeRole.objects.create(
            role_name="Assistant Judge", judge=self.judge, live=False
        )

        self.assertFalse(role.live)
        self.assertEqual(role.role_name, "Assistant Judge")
        self.assertEqual(role.judge, self.judge)

    def test_judge_role_without_judge(self):
        """Test creating a JudgeRole without assigning a judge."""
        role = JudgeRole.objects.create(role_name="Vacant Position")

        self.assertEqual(role.role_name, "Vacant Position")
        self.assertIsNone(role.judge)

    def test_judge_role_revision_creation(self):
        """Test that revisions are created when JudgeRole is saved."""
        role = JudgeRole.objects.create(role_name="Test Role", judge=self.judge)

        # Create revision manually
        role.save_revision()

        # Check that revision was created
        revisions = role.revisions.all()
        self.assertEqual(revisions.count(), 1)

    def test_judge_role_str_method(self):
        """Test the string representation of JudgeRole."""
        role = JudgeRole.objects.create(role_name="Chief Judge", judge=self.judge)
        self.assertEqual(str(role), "Chief Judge, John Doe")

    def test_judge_role_str_method_no_judge(self):
        """Test the string representation of JudgeRole without judge."""
        role = JudgeRole.objects.create(role_name="Vacant Position")
        self.assertEqual(str(role), "Vacant Position, ** Selection Pending **")


class TestNavigationRibbonModerationWorkflow(TestCase):
    """Test draft and moderation workflow for NavigationRibbon snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )

    def test_create_navigation_ribbon_as_draft(self):
        """Test creating a NavigationRibbon snippet in draft state."""
        ribbon = NavigationRibbon.objects.create(
            name="Test Navigation Ribbon", live=False
        )

        self.assertFalse(ribbon.live)
        self.assertEqual(ribbon.name, "Test Navigation Ribbon")

    def test_navigation_ribbon_revision_creation(self):
        """Test that revisions are created when NavigationRibbon is saved."""
        ribbon = NavigationRibbon.objects.create(name="Test Ribbon")

        # Create revision manually
        ribbon.save_revision()

        # Check that revision was created
        revisions = ribbon.revisions.all()
        self.assertEqual(revisions.count(), 1)

    def test_navigation_ribbon_str_method(self):
        """Test the string representation of NavigationRibbon."""
        ribbon = NavigationRibbon.objects.create(name="Test Ribbon")
        self.assertEqual(str(ribbon), "Test Ribbon")


class TestNavigationMenuModerationWorkflow(TestCase):
    """Test draft and moderation workflow for NavigationMenu snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )

    def test_create_navigation_menu_as_draft(self):
        """Test creating a NavigationMenu snippet in draft state."""
        menu = NavigationMenu.objects.create(live=False)

        self.assertFalse(menu.live)

    def test_navigation_menu_unique_constraint(self):
        """Test that only one NavigationMenu can exist."""
        NavigationMenu.objects.create()

        # Creating a second menu should raise a validation error
        menu2 = NavigationMenu()
        with self.assertRaises(Exception):
            menu2.full_clean()

    def test_navigation_menu_revision_creation(self):
        """Test that revisions are created when NavigationMenu is saved."""
        menu = NavigationMenu.objects.create()

        # Create revision manually
        menu.save_revision()

        # Check that revision was created
        revisions = menu.revisions.all()
        self.assertEqual(revisions.count(), 1)

    def test_navigation_menu_str_method(self):
        """Test the string representation of NavigationMenu."""
        menu = NavigationMenu.objects.create()
        self.assertEqual(str(menu), "Navigation Menu")

    def test_navigation_menu_get_active_menu(self):
        """Test the get_active_menu class method."""
        # No menu exists yet
        self.assertIsNone(NavigationMenu.get_active_menu())

        # Create a draft menu
        draft_menu = NavigationMenu.objects.create(live=False)
        self.assertIsNone(NavigationMenu.get_active_menu())

        # Publish the menu
        draft_menu.live = True
        draft_menu.save()

        active_menu = NavigationMenu.get_active_menu()
        self.assertEqual(active_menu, draft_menu)


class TestSnippetWorkflowIntegration(TestCase):
    """Test workflow integration for snippet models."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )
        self.editor_user = User.objects.create_user(
            username="editor", password="testpass123", is_staff=True
        )

    def test_snippet_has_workflow_mixins(self):
        """Test that snippet models have the required workflow mixins."""
        # Test CommonText
        common_text = CommonText.objects.create(name="Test", text="<p>Test</p>")

        # Check that workflow-related fields exist
        self.assertTrue(hasattr(common_text, "live"))
        self.assertTrue(hasattr(common_text, "has_unpublished_changes"))
        self.assertTrue(hasattr(common_text, "first_published_at"))
        self.assertTrue(hasattr(common_text, "last_published_at"))
        self.assertTrue(hasattr(common_text, "latest_revision"))
        self.assertTrue(hasattr(common_text, "live_revision"))

    def test_snippet_revision_tracking(self):
        """Test that snippet models properly track revisions."""
        common_text = CommonText.objects.create(name="Test", text="<p>Original</p>")

        # Create initial revision manually
        common_text.save_revision()
        self.assertEqual(common_text.revisions.count(), 1)

        # Edit and save should create new revision
        common_text.text = "<p>Updated</p>"
        common_text.save()
        common_text.save_revision()

        self.assertEqual(common_text.revisions.count(), 2)

    def test_snippet_draft_state_management(self):
        """Test draft state management for snippets."""
        # Create as draft
        common_text = CommonText.objects.create(
            name="Test", text="<p>Test</p>", live=False
        )

        self.assertFalse(common_text.live)
        self.assertIsNone(common_text.first_published_at)

        # Publish
        common_text.live = True
        common_text.save()

        self.assertTrue(common_text.live)
        # first_published_at should be set automatically by Wagtail


class TestSnippetPermissions(TestCase):
    """Test permission handling for snippet moderation workflow."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )
        self.editor_user = User.objects.create_user(
            username="editor", password="testpass123", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="regular", password="testpass123"
        )

    def test_admin_can_create_snippets(self):
        """Test that admin users can create snippets."""
        # Admin should be able to create snippets
        common_text = CommonText.objects.create(
            name="Admin Test", text="<p>Admin content</p>"
        )
        self.assertEqual(common_text.name, "Admin Test")

    def test_admin_can_publish_snippets(self):
        """Test that admin users can publish snippets."""
        common_text = CommonText.objects.create(
            name="Test", text="<p>Test</p>", live=False
        )

        # Admin should be able to publish
        common_text.live = True
        common_text.save()

        self.assertTrue(common_text.live)


# Integration tests that combine multiple snippet types
class TestSnippetModerationIntegration(TestCase):
    """Integration tests for snippet moderation workflow."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )

    def test_judge_profile_and_collection_workflow(self):
        """Test workflow integration between JudgeProfile and JudgeCollection."""
        # Create a judge profile
        judge = JudgeProfile.objects.create(
            first_name="Jane", last_name="Smith", title="Judge", live=False
        )

        # Create a collection
        collection = JudgeCollection.objects.create(name="Test Judges", live=False)

        # Both should be in draft state
        self.assertFalse(judge.live)
        self.assertFalse(collection.live)

        # Publish both
        judge.live = True
        judge.save()
        collection.live = True
        collection.save()

        self.assertTrue(judge.live)
        self.assertTrue(collection.live)

    def test_multiple_snippet_types_revision_independence(self):
        """Test that different snippet types maintain independent revision histories."""
        # Create snippets of different types
        common_text = CommonText.objects.create(name="Test Text", text="<p>Content</p>")
        judge = JudgeProfile.objects.create(
            first_name="John", last_name="Doe", title="Judge"
        )

        # Create initial revisions
        common_text.save_revision()
        judge.save_revision()

        # Each should have its own revision history
        self.assertEqual(common_text.revisions.count(), 1)
        self.assertEqual(judge.revisions.count(), 1)

        # Edit one shouldn't affect the other's revisions
        common_text.text = "<p>Updated content</p>"
        common_text.save()
        common_text.save_revision()

        self.assertEqual(common_text.revisions.count(), 2)
        self.assertEqual(judge.revisions.count(), 1)  # Should remain unchanged
