"""
Tests for the new card snippet models.

This module tests the SimpleCard and FancyCard snippet models
with their draft and moderation workflow capabilities.
"""

from django.test import TestCase
from django.contrib.auth.models import User

from home.models.snippets.cards import SimpleCard, FancyCard, RelatedPage


class TestSimpleCardSnippet(TestCase):
    """Test SimpleCard snippet functionality."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )

    def test_create_simple_card_as_draft(self):
        """Test creating a SimpleCard snippet in draft state."""
        card = SimpleCard.objects.create(
            card_title="Test Card", card_icon="test-icon", live=False
        )

        self.assertFalse(card.live)
        self.assertEqual(card.card_title, "Test Card")
        self.assertEqual(card.card_icon, "test-icon")

    def test_simple_card_workflow_fields(self):
        """Test that SimpleCard has all required workflow fields."""
        card = SimpleCard.objects.create(card_title="Test Card", card_icon="test-icon")

        # Check workflow fields exist
        self.assertTrue(hasattr(card, "live"))
        self.assertTrue(hasattr(card, "has_unpublished_changes"))
        self.assertTrue(hasattr(card, "first_published_at"))
        self.assertTrue(hasattr(card, "last_published_at"))
        self.assertTrue(hasattr(card, "latest_revision"))
        self.assertTrue(hasattr(card, "live_revision"))
        self.assertTrue(hasattr(card, "go_live_at"))
        self.assertTrue(hasattr(card, "expire_at"))
        self.assertTrue(hasattr(card, "expired"))

    def test_simple_card_publishing_panel(self):
        """Test that SimpleCard includes PublishingPanel."""
        panels = SimpleCard.panels
        panel_names = [panel.__class__.__name__ for panel in panels]

        # Should include PublishingPanel
        self.assertIn("PublishingPanel", panel_names)

    def test_simple_card_revision_creation(self):
        """Test that revisions can be created for SimpleCard."""
        card = SimpleCard.objects.create(card_title="Test Card", card_icon="test-icon")

        # Create initial revision manually
        card.save_revision()

        # Should have one revision
        self.assertEqual(card.revisions.count(), 1)

    def test_simple_card_str_method(self):
        """Test the string representation of SimpleCard."""
        card = SimpleCard.objects.create(card_title="Test Card", card_icon="test-icon")
        self.assertEqual(str(card), "Test Card")

    def test_simple_card_without_title(self):
        """Test SimpleCard string representation without title."""
        card = SimpleCard.objects.create(card_icon="test-icon")
        self.assertTrue(str(card).startswith("Simple Card #"))


class TestFancyCardSnippet(TestCase):
    """Test FancyCard snippet functionality."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_superuser=True
        )

    def test_create_fancy_card_as_draft(self):
        """Test creating a FancyCard snippet in draft state."""
        card = FancyCard.objects.create(
            url="https://example.com", text="Test fancy card text", live=False
        )

        self.assertFalse(card.live)
        self.assertEqual(card.url, "https://example.com")
        self.assertEqual(card.text, "Test fancy card text")

    def test_fancy_card_workflow_fields(self):
        """Test that FancyCard has all required workflow fields."""
        card = FancyCard.objects.create(
            url="https://example.com", text="Test fancy card text"
        )

        # Check workflow fields exist
        self.assertTrue(hasattr(card, "live"))
        self.assertTrue(hasattr(card, "has_unpublished_changes"))
        self.assertTrue(hasattr(card, "first_published_at"))
        self.assertTrue(hasattr(card, "last_published_at"))
        self.assertTrue(hasattr(card, "latest_revision"))
        self.assertTrue(hasattr(card, "live_revision"))
        self.assertTrue(hasattr(card, "go_live_at"))
        self.assertTrue(hasattr(card, "expire_at"))
        self.assertTrue(hasattr(card, "expired"))

    def test_fancy_card_publishing_panel(self):
        """Test that FancyCard includes PublishingPanel."""
        panels = FancyCard.panels
        panel_names = [panel.__class__.__name__ for panel in panels]

        # Should include PublishingPanel
        self.assertIn("PublishingPanel", panel_names)

    def test_fancy_card_str_method_with_text(self):
        """Test FancyCard string representation with text."""
        card = FancyCard.objects.create(
            text="This is a test fancy card with some descriptive text"
        )
        self.assertEqual(
            str(card), "Fancy Card: This is a test fancy card with some descriptive te"
        )

    def test_fancy_card_str_method_without_text(self):
        """Test FancyCard string representation without text."""
        card = FancyCard.objects.create(url="https://example.com")
        self.assertTrue(str(card).startswith("Fancy Card #"))


class TestRelatedPageModel(TestCase):
    """Test RelatedPage model functionality."""

    def test_create_related_page_basic(self):
        """Test creating a basic RelatedPage."""
        card = SimpleCard.objects.create(card_title="Test Card", card_icon="test-icon")

        related_page = RelatedPage.objects.create(
            card=card, display_title="Custom Display Title"
        )

        self.assertEqual(related_page.card, card)
        self.assertEqual(related_page.display_title, "Custom Display Title")

    def test_create_related_page_with_url(self):
        """Test creating a RelatedPage with an external URL."""
        card = SimpleCard.objects.create(card_title="Test Card", card_icon="test-icon")

        related_page = RelatedPage.objects.create(
            card=card, display_title="External Link", url="https://example.com"
        )

        self.assertEqual(related_page.card, card)
        self.assertEqual(related_page.display_title, "External Link")
        self.assertEqual(related_page.url, "https://example.com")
        self.assertIsNone(related_page.related_page)


class TestCardSnippetWorkflow(TestCase):
    """Test workflow functionality for card snippets."""

    def test_card_snippet_live_filtering(self):
        """Test that card snippets can be filtered by live status."""
        # Create draft and published cards
        draft_card = SimpleCard.objects.create(card_title="Draft Card", live=False)

        published_card = SimpleCard.objects.create(
            card_title="Published Card", live=True
        )

        # Test filtering
        draft_cards = SimpleCard.objects.filter(live=False)
        published_cards = SimpleCard.objects.filter(live=True)

        self.assertIn(draft_card, draft_cards)
        self.assertNotIn(draft_card, published_cards)
        self.assertIn(published_card, published_cards)
        self.assertNotIn(published_card, draft_cards)

    def test_card_snippet_moderation_workflow(self):
        """Test the moderation workflow for card snippets."""
        card = SimpleCard.objects.create(card_title="Test Card", live=True)

        # Simulate editing
        card.card_title = "Updated Card Title"
        card.has_unpublished_changes = True
        card.save()

        # Should still be live but have unpublished changes
        self.assertTrue(card.live)
        self.assertTrue(card.has_unpublished_changes)

        # Simulate approving changes
        card.has_unpublished_changes = False
        card.save()

        self.assertTrue(card.live)
        self.assertFalse(card.has_unpublished_changes)
