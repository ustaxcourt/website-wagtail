"""
Real-world scenario tests for snippet draft and moderation workflow.

This module tests practical usage scenarios that administrators would
encounter when using the draft and moderation workflow.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from home.models.snippets.common import CommonText
from home.models.snippets.judges import JudgeProfile, JudgeCollection, JudgeRole
from home.models.snippets.navigation import NavigationRibbon, NavigationMenu


class TestAdministratorWorkflowScenarios(TestCase):
    """Test real-world administrator workflow scenarios."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )
        self.editor_user = User.objects.create_user(
            username="editor", password="testpass123", is_staff=True
        )

    def test_administrator_creates_draft_snippet(self):
        """Test: Administrator creates a snippet and saves it as draft."""
        # Administrator creates a common text snippet as draft
        common_text = CommonText.objects.create(
            name="Legal Notice Draft",
            text="<p>This is a draft legal notice that needs review.</p>",
            live=False,
        )

        # Verify it's in draft state
        self.assertFalse(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)
        self.assertEqual(common_text.name, "Legal Notice Draft")

    def test_administrator_submits_draft_for_moderation(self):
        """Test: Administrator submits a draft snippet for moderation."""
        # Create a draft
        judge_profile = JudgeProfile.objects.create(
            first_name="Sarah",
            last_name="Johnson",
            title="Judge",
            bio="<p>Draft biography awaiting approval.</p>",
            live=False,
        )

        # Simulate submitting for moderation (marking for review)
        judge_profile.has_unpublished_changes = True
        judge_profile.save()

        # Verify submission state
        self.assertFalse(judge_profile.live)
        self.assertTrue(judge_profile.has_unpublished_changes)

    def test_administrator_approves_moderation_request(self):
        """Test: Administrator reviews and approves a moderation request."""
        # Create a snippet with changes awaiting approval
        navigation_ribbon = NavigationRibbon.objects.create(
            name="Emergency Notice Ribbon", live=False, has_unpublished_changes=True
        )

        # Administrator approves and publishes
        navigation_ribbon.live = True
        navigation_ribbon.has_unpublished_changes = False
        navigation_ribbon.save()

        # Verify approval
        self.assertTrue(navigation_ribbon.live)
        self.assertFalse(navigation_ribbon.has_unpublished_changes)

    def test_administrator_rejects_moderation_request(self):
        """Test: Administrator rejects a moderation request."""
        # Create snippet with changes awaiting approval
        common_text = CommonText.objects.create(
            name="Policy Update",
            text="<p>This policy update needs revision.</p>",
            live=False,
            has_unpublished_changes=True,
        )

        # Administrator rejects by resetting to draft state
        common_text.has_unpublished_changes = False
        common_text.save()

        # Verify rejection (back to draft state)
        self.assertFalse(common_text.live)
        self.assertFalse(common_text.has_unpublished_changes)

    def test_administrator_edits_published_snippet(self):
        """Test: Administrator edits an already published snippet."""
        # Create and publish a snippet
        judge_role = JudgeRole.objects.create(
            role_name="Assistant Chief Judge", live=True
        )

        # Verify initial published state
        self.assertTrue(judge_role.live)
        self.assertFalse(judge_role.has_unpublished_changes)

        # Administrator makes edits
        judge_role.role_name = "Senior Assistant Chief Judge"
        judge_role.has_unpublished_changes = True
        judge_role.save()

        # Verify edited state (still live but with unpublished changes)
        self.assertTrue(judge_role.live)
        self.assertTrue(judge_role.has_unpublished_changes)

    def test_administrator_schedules_publication(self):
        """Test: Administrator schedules snippet for future publication."""
        future_date = timezone.now() + timezone.timedelta(days=1)

        # Create snippet scheduled for future publication
        common_text = CommonText.objects.create(
            name="Holiday Schedule Notice",
            text="<p>The court will be closed for the holiday.</p>",
            live=False,
            go_live_at=future_date,
        )

        # Verify scheduling
        self.assertFalse(common_text.live)
        self.assertEqual(common_text.go_live_at, future_date)

    def test_administrator_schedules_expiry(self):
        """Test: Administrator schedules snippet to expire automatically."""
        future_expiry = timezone.now() + timezone.timedelta(days=30)

        # Create snippet with expiry date
        navigation_ribbon = NavigationRibbon.objects.create(
            name="Temporary Notice", live=True, expire_at=future_expiry
        )

        # Verify expiry scheduling
        self.assertTrue(navigation_ribbon.live)
        self.assertEqual(navigation_ribbon.expire_at, future_expiry)
        self.assertFalse(navigation_ribbon.expired)


class TestJudgeProfileWorkflowScenarios(TestCase):
    """Test specific scenarios for judge profile management."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", is_staff=True, is_superuser=True
        )

    def test_create_judge_profile_with_careful_review(self):
        """
        Test: Creating a judge profile that requires careful language review.
        This addresses the user requirement for saving judge profiles as drafts
        because "it is very important to get the language when adding or editing
        a judge profile."
        """
        # Administrator creates a judge profile as draft for review
        judge_profile = JudgeProfile.objects.create(
            first_name="Honorable",
            last_name="Mitchell",
            title="Senior Judge",
            bio="<p>Judge Mitchell has served with distinction for over 20 years...</p>",
            chambers_telephone="555-0199",
            live=False,  # Saved as draft for language review
        )

        # Verify it's saved as draft
        self.assertFalse(judge_profile.live)
        self.assertEqual(judge_profile.first_name, "Honorable")
        self.assertEqual(judge_profile.title, "Senior Judge")

        # Administrator reviews and makes language adjustments
        judge_profile.bio = "<p>The Honorable Judge Mitchell has served with distinction for over 20 years...</p>"
        judge_profile.save()

        # Still in draft for further review if needed
        self.assertFalse(judge_profile.live)

        # Finally publish after language review is complete
        judge_profile.live = True
        judge_profile.save()

        self.assertTrue(judge_profile.live)

    def test_edit_existing_judge_profile_for_language_review(self):
        """Test: Editing an existing judge profile with language review workflow."""
        # Create existing published judge profile
        judge_profile = JudgeProfile.objects.create(
            first_name="Robert",
            last_name="Adams",
            title="Judge",
            bio="<p>Judge Adams specializes in tax law.</p>",
            live=True,
        )

        # Administrator makes edits but keeps as draft for language review
        judge_profile.bio = "<p>The Honorable Judge Adams specializes in complex tax law matters and has extensive experience in corporate tax disputes.</p>"
        judge_profile.has_unpublished_changes = True
        judge_profile.save()

        # Verify edited state (published version remains live, but changes are unpublished)
        self.assertTrue(judge_profile.live)
        self.assertTrue(judge_profile.has_unpublished_changes)

        # After language review, administrator publishes changes
        judge_profile.has_unpublished_changes = False
        judge_profile.save()

        # Verify final published state
        self.assertTrue(judge_profile.live)
        self.assertFalse(judge_profile.has_unpublished_changes)

    def test_judge_collection_moderation_workflow(self):
        """Test: Managing judge collections with moderation workflow."""
        # Create a collection as draft
        collection = JudgeCollection.objects.create(name="Visiting Judges", live=False)

        # Create judge profiles for the collection
        JudgeProfile.objects.create(
            first_name="Alice", last_name="Brown", title="Visiting Judge", live=True
        )

        JudgeProfile.objects.create(
            first_name="David", last_name="Wilson", title="Visiting Judge", live=True
        )

        # Verify collection is still draft
        self.assertFalse(collection.live)

        # Administrator reviews and publishes collection
        collection.live = True
        collection.save()

        self.assertTrue(collection.live)


class TestNavigationWorkflowScenarios(TestCase):
    """Test navigation-specific workflow scenarios."""

    def test_navigation_menu_update_workflow(self):
        """Test: Updating the navigation menu with moderation workflow."""
        # Create navigation menu (only one allowed)
        menu = NavigationMenu.objects.create(live=True)

        # Verify it's live
        self.assertTrue(menu.live)

        # Administrator makes changes but saves as draft for review
        menu.live = False
        menu.has_unpublished_changes = True
        menu.save()

        # Verify draft state with changes
        self.assertFalse(menu.live)
        self.assertTrue(menu.has_unpublished_changes)

        # After review, publish changes
        menu.live = True
        menu.has_unpublished_changes = False
        menu.save()

        self.assertTrue(menu.live)
        self.assertFalse(menu.has_unpublished_changes)

    def test_navigation_ribbon_emergency_notice(self):
        """Test: Creating emergency notice ribbon with immediate publication."""
        # Create emergency notice that needs immediate publication
        emergency_ribbon = NavigationRibbon.objects.create(
            name="Court Closure Emergency Notice",
            live=True,  # Published immediately due to emergency
        )

        # Verify immediate publication
        self.assertTrue(emergency_ribbon.live)

        # Later, update with expiry date
        emergency_ribbon.expire_at = timezone.now() + timezone.timedelta(days=1)
        emergency_ribbon.save()

        # Verify it's still live but will expire
        self.assertTrue(emergency_ribbon.live)
        self.assertIsNotNone(emergency_ribbon.expire_at)


class TestWorkflowStateValidation(TestCase):
    """Test validation of workflow states and transitions."""

    def test_snippet_state_consistency(self):
        """Test that snippet states remain consistent during workflow operations."""
        # Create snippet in various states and verify consistency

        # Draft state
        draft_text = CommonText.objects.create(
            name="Draft Text",
            text="<p>Draft content</p>",
            live=False,
            has_unpublished_changes=False,
        )

        self.assertFalse(draft_text.live)
        self.assertFalse(draft_text.has_unpublished_changes)

        # Published state
        published_text = CommonText.objects.create(
            name="Published Text",
            text="<p>Published content</p>",
            live=True,
            has_unpublished_changes=False,
        )

        self.assertTrue(published_text.live)
        self.assertFalse(published_text.has_unpublished_changes)

        # Published with unpublished changes
        modified_text = CommonText.objects.create(
            name="Modified Text",
            text="<p>Modified content</p>",
            live=True,
            has_unpublished_changes=True,
        )

        self.assertTrue(modified_text.live)
        self.assertTrue(modified_text.has_unpublished_changes)

    def test_workflow_with_multiple_snippet_types(self):
        """Test workflow with multiple different snippet types simultaneously."""
        # Create multiple snippet types in different states
        common_text = CommonText.objects.create(
            name="Common Text", text="<p>Content</p>", live=False
        )

        judge = JudgeProfile.objects.create(
            first_name="Test", last_name="Judge", title="Judge", live=True
        )

        collection = JudgeCollection.objects.create(
            name="Test Collection", live=False, has_unpublished_changes=True
        )

        # Verify each maintains its own state
        self.assertFalse(common_text.live)
        self.assertTrue(judge.live)
        self.assertFalse(collection.live)
        self.assertTrue(collection.has_unpublished_changes)

        # Modify states independently
        common_text.live = True
        common_text.save()

        judge.has_unpublished_changes = True
        judge.save()

        collection.live = True
        collection.has_unpublished_changes = False
        collection.save()

        # Verify independent state changes
        self.assertTrue(common_text.live)
        self.assertTrue(judge.live)
        self.assertTrue(judge.has_unpublished_changes)
        self.assertTrue(collection.live)
        self.assertFalse(collection.has_unpublished_changes)
