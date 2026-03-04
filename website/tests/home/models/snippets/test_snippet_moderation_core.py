"""
Core tests for snippet draft and moderation workflow functionality.

This module tests the essential draft status and moderation workflow
functionality for all snippet models.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from home.models.snippets.common import CommonText
from home.models.snippets.judges import JudgeProfile, JudgeCollection, JudgeRole
from home.models.snippets.navigation import NavigationRibbon, NavigationMenu


class TestSnippetDraftModerationCore(TestCase):
    """Core tests for snippet draft and moderation functionality."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )

    def test_all_snippet_models_have_workflow_fields(self):
        """Test that all snippet models have required workflow fields."""
        snippet_models = [
            CommonText,
            JudgeProfile,
            JudgeCollection,
            JudgeRole,
            NavigationRibbon,
            NavigationMenu,
        ]

        for model in snippet_models:
            # Create an instance to test field access
            if model == CommonText:
                instance = model(name="Test", text="<p>Test</p>")
            elif model == JudgeProfile:
                instance = model(first_name="Test", last_name="User", title="Judge")
            elif model == JudgeCollection:
                instance = model(name="Test Collection")
            elif model == JudgeRole:
                instance = model(role_name="Test Role")
            elif model == NavigationRibbon:
                instance = model(name="Test Ribbon")
            elif model == NavigationMenu:
                instance = model()

            # Test that workflow fields exist
            self.assertTrue(hasattr(instance, "live"))
            self.assertTrue(hasattr(instance, "has_unpublished_changes"))
            self.assertTrue(hasattr(instance, "first_published_at"))
            self.assertTrue(hasattr(instance, "last_published_at"))
            self.assertTrue(hasattr(instance, "latest_revision"))
            self.assertTrue(hasattr(instance, "live_revision"))
            self.assertTrue(hasattr(instance, "go_live_at"))
            self.assertTrue(hasattr(instance, "expire_at"))
            self.assertTrue(hasattr(instance, "expired"))

    def test_common_text_draft_functionality(self):
        """Test CommonText draft functionality."""
        # Create as draft
        common_text = CommonText.objects.create(
            name="Draft Text", text="<p>Draft content</p>", live=False
        )

        self.assertFalse(common_text.live)
        self.assertEqual(common_text.name, "Draft Text")

        # Publish
        common_text.live = True
        common_text.save()

        self.assertTrue(common_text.live)

    def test_judge_profile_draft_functionality(self):
        """Test JudgeProfile draft functionality."""
        # Create as draft
        judge = JudgeProfile.objects.create(
            first_name="Jane", last_name="Smith", title="Judge", live=False
        )

        self.assertFalse(judge.live)
        self.assertEqual(judge.first_name, "Jane")

        # Publish
        judge.live = True
        judge.save()

        self.assertTrue(judge.live)

    def test_judge_collection_draft_functionality(self):
        """Test JudgeCollection draft functionality."""
        # Create as draft
        collection = JudgeCollection.objects.create(name="Draft Collection", live=False)

        self.assertFalse(collection.live)
        self.assertEqual(collection.name, "Draft Collection")

        # Publish
        collection.live = True
        collection.save()

        self.assertTrue(collection.live)

    def test_judge_role_draft_functionality(self):
        """Test JudgeRole draft functionality."""
        judge = JudgeProfile.objects.create(
            first_name="Test", last_name="Judge", title="Judge"
        )

        # Create as draft
        role = JudgeRole.objects.create(
            role_name="Assistant Judge", judge=judge, live=False
        )

        self.assertFalse(role.live)
        self.assertEqual(role.role_name, "Assistant Judge")

        # Publish
        role.live = True
        role.save()

        self.assertTrue(role.live)

    def test_navigation_ribbon_draft_functionality(self):
        """Test NavigationRibbon draft functionality."""
        # Create as draft
        ribbon = NavigationRibbon.objects.create(name="Draft Ribbon", live=False)

        self.assertFalse(ribbon.live)
        self.assertEqual(ribbon.name, "Draft Ribbon")

        # Publish
        ribbon.live = True
        ribbon.save()

        self.assertTrue(ribbon.live)

    def test_navigation_menu_draft_functionality(self):
        """Test NavigationMenu draft functionality."""
        # Create as draft
        menu = NavigationMenu.objects.create(live=False)

        self.assertFalse(menu.live)

        # Publish
        menu.live = True
        menu.save()

        self.assertTrue(menu.live)

    def test_snippet_unpublished_changes_flag(self):
        """Test the has_unpublished_changes flag functionality."""
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

    def test_snippet_managers_have_live_methods(self):
        """Test that snippet managers can filter by live status."""
        snippet_models = [
            CommonText,
            JudgeProfile,
            JudgeCollection,
            JudgeRole,
            NavigationRibbon,
            NavigationMenu,
        ]

        for model in snippet_models:
            # Test that we can filter by live status
            # This verifies that the manager supports DraftStateMixin fields
            try:
                model.objects.filter(live=True)
                model.objects.filter(live=False)
                # If we can filter by live, the manager is working correctly
                self.assertTrue(True)
            except Exception:
                self.fail(f"Model {model.__name__} cannot filter by live status")

    def test_snippet_string_representations(self):
        """Test string representations of snippet models."""
        # CommonText
        common_text = CommonText.objects.create(name="Test Text", text="<p>Test</p>")
        self.assertEqual(str(common_text), "Test Text")

        # JudgeProfile
        judge = JudgeProfile.objects.create(
            first_name="John", last_name="Doe", title="Judge", display_name="John Doe"
        )
        self.assertEqual(str(judge), "John Doe")

        # JudgeCollection
        collection = JudgeCollection.objects.create(name="Test Collection")
        self.assertEqual(str(collection), "Test Collection")

        # JudgeRole
        role = JudgeRole.objects.create(role_name="Test Role", judge=judge)
        self.assertEqual(str(role), "Test Role, John Doe")

        # NavigationRibbon
        ribbon = NavigationRibbon.objects.create(name="Test Ribbon")
        self.assertEqual(str(ribbon), "Test Ribbon")

        # NavigationMenu
        menu = NavigationMenu.objects.create()
        self.assertEqual(str(menu), "Navigation Menu")

    def test_judge_profile_display_name_generation(self):
        """Test JudgeProfile display name auto-generation."""
        judge = JudgeProfile.objects.create(
            first_name="John",
            middle_initial="A",
            last_name="Doe",
            suffix="Jr.",
            title="Judge",
        )

        # Display name should be auto-generated
        self.assertEqual(judge.display_name, "John A Doe Jr.")

    def test_navigation_menu_unique_constraint(self):
        """Test NavigationMenu unique constraint."""
        # Create first menu
        NavigationMenu.objects.create()

        # Creating second menu should fail
        menu2 = NavigationMenu()
        with self.assertRaises(Exception):
            menu2.full_clean()

    def test_navigation_menu_get_active_menu(self):
        """Test NavigationMenu get_active_menu method."""
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


class TestSnippetAdminPanelIntegration(TestCase):
    """Test that snippet models have proper admin panel integration."""

    def test_all_snippets_have_publishing_panel(self):
        """Test that all snippet models include PublishingPanel."""
        snippet_models_and_names = [
            (CommonText, "CommonText"),
            (JudgeProfile, "JudgeProfile"),
            (JudgeCollection, "JudgeCollection"),
            (JudgeRole, "JudgeRole"),
            (NavigationRibbon, "NavigationRibbon"),
            (NavigationMenu, "NavigationMenu"),
        ]

        for model, name in snippet_models_and_names:
            with self.subTest(model=name):
                # Check that the model has panels
                self.assertTrue(hasattr(model, "panels"))

                # Check that panels is not empty
                self.assertGreater(len(model.panels), 0)

                # Check for PublishingPanel - look for the class name in panel types
                panel_types = [type(panel).__name__ for panel in model.panels]
                self.assertIn("PublishingPanel", panel_types)

    def test_snippets_maintain_existing_panels(self):
        """Test that existing panels are preserved alongside PublishingPanel."""
        # CommonText should have FieldPanel for name and text
        common_text_panels = [type(panel).__name__ for panel in CommonText.panels]
        self.assertIn("FieldPanel", common_text_panels)
        self.assertIn("PublishingPanel", common_text_panels)

        # JudgeCollection should have InlinePanel for judges
        judge_collection_panels = [
            type(panel).__name__ for panel in JudgeCollection.panels
        ]
        self.assertIn("InlinePanel", judge_collection_panels)
        self.assertIn("PublishingPanel", judge_collection_panels)

        # NavigationRibbon should have InlinePanel for links
        nav_ribbon_panels = [type(panel).__name__ for panel in NavigationRibbon.panels]
        self.assertIn("InlinePanel", nav_ribbon_panels)
        self.assertIn("PublishingPanel", nav_ribbon_panels)


class TestSnippetWorkflowBehavior(TestCase):
    """Test snippet workflow behavior and state transitions."""

    def test_snippet_workflow_state_transitions(self):
        """Test various workflow state transitions."""
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Test content</p>", live=False
        )

        # Start as draft
        self.assertFalse(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)

        # Transition to published
        common_text.live = True
        common_text.save()

        self.assertTrue(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)

        # Edit while published
        common_text.text = "<p>Updated content</p>"
        common_text.has_unpublished_changes = True
        common_text.save()

        self.assertTrue(common_text.live)
        self.assertTrue(common_text.has_unpublished_changes)

        # Unpublish
        common_text.live = False
        common_text.save()

        self.assertFalse(common_text.live)

    def test_snippet_workflow_with_scheduling(self):
        """Test snippet workflow with scheduled publishing and expiry."""
        future_publish = timezone.now() + timezone.timedelta(hours=1)
        future_expire = timezone.now() + timezone.timedelta(days=1)

        common_text = CommonText.objects.create(
            name="Scheduled Text",
            text="<p>Scheduled content</p>",
            live=False,
            go_live_at=future_publish,
            expire_at=future_expire,
        )

        self.assertFalse(common_text.live)
        self.assertEqual(common_text.go_live_at, future_publish)
        self.assertEqual(common_text.expire_at, future_expire)
        self.assertFalse(common_text.expired)

    def test_multiple_snippet_types_independence(self):
        """Test that different snippet types work independently."""
        # Create different types of snippets
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Content</p>", live=False
        )
        judge = JudgeProfile.objects.create(
            first_name="John", last_name="Doe", title="Judge", live=True
        )
        collection = JudgeCollection.objects.create(name="Test Collection", live=False)

        # Each should maintain its own state
        self.assertFalse(common_text.live)
        self.assertTrue(judge.live)
        self.assertFalse(collection.live)

        # Publishing one shouldn't affect others
        common_text.live = True
        common_text.save()

        self.assertTrue(common_text.live)
        self.assertTrue(judge.live)  # unchanged
        self.assertFalse(collection.live)  # unchanged
