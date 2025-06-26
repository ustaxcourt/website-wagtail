"""
Tests for snippet admin integration and workflow UI functionality.

This module tests the admin interface integration for snippet models
with draft and moderation workflow capabilities.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User

from home.models.snippets.common import CommonText
from home.models.snippets.judges import JudgeProfile, JudgeCollection, JudgeRole
from home.models.snippets.navigation import NavigationRibbon, NavigationMenu


class TestSnippetAdminAccess(TestCase):
    """Test admin access and permissions for snippet models."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )
        self.editor_user = User.objects.create_user(
            username="editor", password="testpass123", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="regular", password="testpass123"
        )

    def test_admin_user_exists(self):
        """Test that admin user can be created."""
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_superuser)

    def test_editor_user_exists(self):
        """Test that editor user can be created."""
        self.assertTrue(self.editor_user.is_staff)
        self.assertFalse(self.editor_user.is_superuser)

    def test_regular_user_exists(self):
        """Test that regular user has correct permissions."""
        self.assertFalse(self.regular_user.is_staff)
        self.assertFalse(self.regular_user.is_superuser)


class TestCommonTextAdminWorkflow(TestCase):
    """Test admin workflow for CommonText snippets."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )
        self.client.login(username="admin", password="testpass123")

    def test_create_common_text_snippet(self):
        """Test creating a CommonText snippet."""
        common_text = CommonText.objects.create(
            name="Admin Test", text="<p>Admin created content</p>"
        )
        self.assertEqual(common_text.name, "Admin Test")

    def test_common_text_has_publishing_panel(self):
        """Test that CommonText model includes PublishingPanel."""
        from home.models.snippets.common import CommonText

        # Check that the model has the required panels
        panels = CommonText.panels
        panel_names = [panel.__class__.__name__ for panel in panels]

        # Should include PublishingPanel
        self.assertIn("PublishingPanel", panel_names)

    def test_common_text_has_workflow_fields(self):
        """Test that CommonText has all required workflow fields."""
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Test content</p>"
        )

        # Check workflow fields exist
        self.assertTrue(hasattr(common_text, "live"))
        self.assertTrue(hasattr(common_text, "has_unpublished_changes"))
        self.assertTrue(hasattr(common_text, "first_published_at"))
        self.assertTrue(hasattr(common_text, "last_published_at"))
        self.assertTrue(hasattr(common_text, "latest_revision"))
        self.assertTrue(hasattr(common_text, "live_revision"))
        self.assertTrue(hasattr(common_text, "go_live_at"))
        self.assertTrue(hasattr(common_text, "expire_at"))
        self.assertTrue(hasattr(common_text, "expired"))


class TestJudgeProfileAdminWorkflow(TestCase):
    """Test admin workflow for JudgeProfile snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )

    def test_judge_profile_has_publishing_panel(self):
        """Test that JudgeProfile model includes PublishingPanel."""
        from home.models.snippets.judges import JudgeProfile

        # Check that the model has the required panels
        panels = JudgeProfile.panels
        panel_names = [panel.__class__.__name__ for panel in panels]

        # Should include PublishingPanel
        self.assertIn("PublishingPanel", panel_names)

    def test_judge_profile_workflow_integration(self):
        """Test JudgeProfile workflow integration."""
        judge = JudgeProfile.objects.create(
            first_name="John", last_name="Doe", title="Judge", live=False
        )

        # Should start as draft
        self.assertFalse(judge.live)

        # Should be able to publish
        judge.live = True
        judge.save()

        self.assertTrue(judge.live)

    def test_judge_profile_search_functionality(self):
        """Test that JudgeProfile maintains its search functionality."""
        from home.models.snippets.judges import JudgeProfile

        # Check that search fields are still defined
        self.assertTrue(hasattr(JudgeProfile, "search_fields"))
        self.assertGreater(len(JudgeProfile.search_fields), 0)


class TestJudgeCollectionAdminWorkflow(TestCase):
    """Test admin workflow for JudgeCollection snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )

    def test_judge_collection_has_publishing_panel(self):
        """Test that JudgeCollection model includes PublishingPanel."""

        # Check that the model has the required panels
        panels = JudgeCollection.panels
        panel_names = [panel.__class__.__name__ for panel in panels]

        # Should include PublishingPanel
        self.assertIn("PublishingPanel", panel_names)

    def test_judge_collection_inline_panels(self):
        """Test that JudgeCollection maintains its inline panels."""

        # Check that inline panels are present
        panels = JudgeCollection.panels
        panel_names = [panel.__class__.__name__ for panel in panels]

        # Should include InlinePanel for judges
        self.assertIn("InlinePanel", panel_names)


class TestJudgeRoleAdminWorkflow(TestCase):
    """Test admin workflow for JudgeRole snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )
        self.judge = JudgeProfile.objects.create(
            first_name="Test", last_name="Judge", title="Judge"
        )

    def test_judge_role_has_publishing_panel(self):
        """Test that JudgeRole model includes PublishingPanel."""
        from home.models.snippets.judges import JudgeRole

        # Check that the model has the required panels
        panels = JudgeRole.panels
        panel_names = [panel.__class__.__name__ for panel in panels]

        # Should include PublishingPanel
        self.assertIn("PublishingPanel", panel_names)

    def test_judge_role_validation_with_workflow(self):
        """Test that JudgeRole validation works with workflow."""
        # Test creating restricted role
        role = JudgeRole.objects.create(
            role_name="Chief Judge", judge=self.judge, live=False
        )

        self.assertEqual(role.role_name, "Chief Judge")
        self.assertFalse(role.live)

        # Should be able to publish
        role.live = True
        role.save()

        self.assertTrue(role.live)


class TestNavigationSnippetAdminWorkflow(TestCase):
    """Test admin workflow for Navigation snippet models."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )

    def test_navigation_ribbon_has_publishing_panel(self):
        """Test that NavigationRibbon model includes PublishingPanel."""

        # Check that the model has the required panels
        panels = NavigationRibbon.panels
        panel_names = [panel.__class__.__name__ for panel in panels]

        # Should include PublishingPanel
        self.assertIn("PublishingPanel", panel_names)

    def test_navigation_menu_has_publishing_panel(self):
        """Test that NavigationMenu model includes PublishingPanel."""
        from home.models.snippets.navigation import NavigationMenu

        # Check that the model has the required panels
        panels = NavigationMenu.panels
        panel_names = [panel.__class__.__name__ for panel in panels]

        # Should include PublishingPanel
        self.assertIn("PublishingPanel", panel_names)

    def test_navigation_menu_unique_constraint_with_workflow(self):
        """Test NavigationMenu unique constraint works with workflow."""
        # Create first menu
        menu1 = NavigationMenu.objects.create(live=False)
        self.assertFalse(menu1.live)

        # Attempting to create second menu should still fail
        menu2 = NavigationMenu()
        with self.assertRaises(Exception):
            menu2.full_clean()

    def test_navigation_menu_preview_functionality(self):
        """Test that NavigationMenu maintains preview functionality."""
        from home.models.snippets.navigation import NavigationMenu

        menu = NavigationMenu.objects.create()

        # Should have preview methods
        self.assertTrue(hasattr(menu, "get_preview_template"))
        self.assertTrue(hasattr(menu, "get_preview_context"))

        # Test preview template method
        template = menu.get_preview_template(None, "default")
        self.assertEqual(template, "previews/header_preview.html")


class TestSnippetWorkflowUIIntegration(TestCase):
    """Test workflow UI integration for snippets."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )

    def test_snippet_models_have_required_mixins(self):
        """Test that all snippet models have the required workflow mixins."""
        from home.models.snippets.common import CommonText
        from home.models.snippets.judges import JudgeProfile, JudgeRole
        from home.models.snippets.navigation import NavigationRibbon, NavigationMenu

        snippet_models = [
            CommonText,
            JudgeProfile,
            JudgeCollection,
            JudgeRole,
            NavigationRibbon,
            NavigationMenu,
        ]

        for model in snippet_models:
            # Check that the model has workflow-related fields
            instance = model()

            self.assertTrue(hasattr(instance, "live"))
            self.assertTrue(hasattr(instance, "has_unpublished_changes"))
            self.assertTrue(hasattr(instance, "latest_revision"))
            self.assertTrue(hasattr(instance, "live_revision"))

    def test_snippet_models_have_page_query_set_manager(self):
        """Test that snippet models can filter by live status."""
        from home.models.snippets.common import CommonText
        from home.models.snippets.judges import JudgeProfile, JudgeRole
        from home.models.snippets.navigation import NavigationRibbon, NavigationMenu

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
            try:
                model.objects.filter(live=True)
                model.objects.filter(live=False)
                # If we can filter by live, the manager is working correctly
                self.assertTrue(True)
            except Exception:
                self.fail(f"Model {model.__name__} cannot filter by live status")

    def test_snippet_models_have_revisions_property(self):
        """Test that snippet models have revisions property."""
        from home.models.snippets.common import CommonText

        # Test with CommonText as representative
        common_text = CommonText.objects.create(name="Test", text="<p>Test</p>")

        # Should have revisions property
        self.assertTrue(hasattr(common_text, "revisions"))
        self.assertIsNotNone(common_text.revisions)

    def test_snippet_workflow_field_integration(self):
        """Test that workflow fields are properly integrated."""
        common_text = CommonText.objects.create(
            name="Test Text", text="<p>Test content</p>", live=False
        )

        # Test all workflow fields
        self.assertFalse(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)
        self.assertFalse(common_text.expired)
        self.assertIsNone(common_text.go_live_at)
        self.assertIsNone(common_text.expire_at)
        self.assertIsNone(common_text.first_published_at)
        self.assertIsNone(common_text.last_published_at)


class TestSnippetAdminFormIntegration(TestCase):
    """Test admin form integration for snippet workflow."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )

    def test_publishing_panel_integration(self):
        """Test that PublishingPanel is properly integrated in all snippet models."""
        from home.models.snippets.common import CommonText
        from home.models.snippets.judges import JudgeProfile, JudgeRole
        from home.models.snippets.navigation import NavigationRibbon, NavigationMenu

        snippet_models = [
            CommonText,
            JudgeProfile,
            JudgeCollection,
            JudgeRole,
            NavigationRibbon,
            NavigationMenu,
        ]

        for model in snippet_models:
            panels = model.panels
            panel_types = [type(panel).__name__ for panel in panels]

            # Each model should have PublishingPanel
            self.assertIn("PublishingPanel", panel_types)

    def test_field_panels_preserved(self):
        """Test that existing field panels are preserved alongside PublishingPanel."""
        from home.models.snippets.common import CommonText

        panels = CommonText.panels
        panel_types = [type(panel).__name__ for panel in panels]

        # Should have both FieldPanel and PublishingPanel
        self.assertIn("FieldPanel", panel_types)
        self.assertIn("PublishingPanel", panel_types)

    def test_inline_panels_preserved(self):
        """Test that inline panels are preserved in models that use them."""
        from home.models.snippets.navigation import NavigationRibbon

        # JudgeCollection should have InlinePanel for judges
        collection_panels = JudgeCollection.panels
        collection_panel_types = [type(panel).__name__ for panel in collection_panels]
        self.assertIn("InlinePanel", collection_panel_types)
        self.assertIn("PublishingPanel", collection_panel_types)

        # NavigationRibbon should have InlinePanel for links
        ribbon_panels = NavigationRibbon.panels
        ribbon_panel_types = [type(panel).__name__ for panel in ribbon_panels]
        self.assertIn("InlinePanel", ribbon_panel_types)
        self.assertIn("PublishingPanel", ribbon_panel_types)
