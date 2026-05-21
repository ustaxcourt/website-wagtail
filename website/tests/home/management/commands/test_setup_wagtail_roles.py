"""Tests for home/management/commands/setup_wagtail_roles.py"""

import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import Group


@pytest.mark.django_db
class TestSetupWagtailRoles:
    def _setup_wagtail_collections(self):
        """Create the root Collection that Wagtail requires."""
        from wagtail.models import Collection

        if not Collection.objects.exists():
            Collection.add_root(name="Root")

    def test_handle_creates_groups(self):
        """Test the command creates expected groups."""
        self._setup_wagtail_collections()
        from wagtail.models import Page

        mock_root = MagicMock()
        mock_root.slug = "root"
        mock_root.specific = mock_root
        with patch.object(Page, "get_first_root_node", return_value=mock_root):
            from django.core.management import call_command

            out = StringIO()
            call_command("setup_wagtail_roles", stdout=out)
        # At minimum, common groups should be created
        assert Group.objects.filter(name="Editors").exists()
        assert Group.objects.filter(name="Moderators").exists()

    def test_handle_is_idempotent(self):
        """Running twice should not fail."""
        self._setup_wagtail_collections()
        from wagtail.models import Page

        mock_root = MagicMock()
        mock_root.slug = "root"
        mock_root.specific = mock_root
        with patch.object(Page, "get_first_root_node", return_value=mock_root):
            from django.core.management import call_command

            call_command("setup_wagtail_roles", stdout=StringIO())
            call_command("setup_wagtail_roles", stdout=StringIO())
        assert Group.objects.filter(name="Editors").exists()


@pytest.mark.django_db
class TestSetupSnippetPermissions:
    def test_setup_snippet_permissions_group_not_found_skips(self):
        """When group does not exist, logs warning and skips."""
        from home.management.commands.setup_wagtail_roles import Command

        cmd = Command.__new__(Command)
        out = StringIO()
        cmd.stdout = out
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        cmd.style.WARNING = lambda x: x

        # Don't create any groups — all should be skipped
        Group.objects.filter(
            name__in=["Editors", "Moderators", "Chief Judge Moderator"]
        ).delete()
        cmd.setup_snippet_permissions()
        output = out.getvalue()
        assert "not found" in output or "skipping" in output

    def test_setup_snippet_permissions_with_group_exists(self):
        """When groups exist, grants snippet permissions."""
        from wagtail.models import Collection

        if not Collection.objects.exists():
            Collection.add_root(name="Root")
        from home.management.commands.setup_wagtail_roles import Command

        cmd = Command.__new__(Command)
        out = StringIO()
        cmd.stdout = out
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        cmd.style.WARNING = lambda x: x

        editors_group, _ = Group.objects.get_or_create(name="Editors")
        initial_permission_count = editors_group.permissions.count()

        cmd.setup_snippet_permissions()

        editors_group.refresh_from_db()
        assert editors_group.permissions.count() > 0
        assert editors_group.permissions.count() > initial_permission_count


@pytest.mark.django_db
class TestSetupSnippetWorkflow:
    def test_setup_snippet_workflow_no_workflow(self):
        """When no workflow found, logs warning and returns."""
        from home.management.commands.setup_wagtail_roles import Command
        from wagtail.models import Workflow

        cmd = Command.__new__(Command)
        out = StringIO()
        cmd.stdout = out
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        cmd.style.WARNING = lambda x: x
        cmd.setup_chief_judge_workflow = MagicMock()

        Workflow.objects.filter(name="Moderators approval").delete()
        cmd.setup_snippet_workflow()
        output = out.getvalue()
        assert "not found" in output or "skipping" in output

    def test_setup_snippet_workflow_with_workflow(self):
        """When workflow exists, assigns snippet models."""
        from wagtail.models import Collection

        if not Collection.objects.exists():
            Collection.add_root(name="Root")
        from home.management.commands.setup_wagtail_roles import Command
        from wagtail.models import Workflow, Task, WorkflowTask

        cmd = Command.__new__(Command)
        out = StringIO()
        cmd.stdout = out
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        cmd.style.WARNING = lambda x: x
        cmd.setup_chief_judge_workflow = MagicMock()

        # Create a simple workflow
        task = Task.objects.first()
        if not task:
            from wagtail.models import GroupApprovalTask

            task = GroupApprovalTask.objects.create(name="Test Task")
        workflow, _ = Workflow.objects.get_or_create(name="Moderators approval")
        if not WorkflowTask.objects.filter(workflow=workflow).exists():
            WorkflowTask.objects.create(workflow=workflow, task=task, sort_order=1)

        from wagtail.models import WorkflowContentType

        cmd.setup_snippet_workflow()

        cmd.setup_chief_judge_workflow.assert_called_once()
        assert WorkflowContentType.objects.filter(workflow=workflow).exists()


@pytest.mark.django_db
class TestSetupChiefJudgeWorkflow:
    def test_setup_chief_judge_workflow_no_workflow(self):
        """When no workflow, logs warning and returns."""
        from home.management.commands.setup_wagtail_roles import Command
        from wagtail.models import Workflow

        cmd = Command.__new__(Command)
        out = StringIO()
        cmd.stdout = out
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        cmd.style.WARNING = lambda x: x

        Workflow.objects.filter(name="Moderators approval").delete()
        cmd.setup_chief_judge_workflow()
        output = out.getvalue()
        assert "not found" in output or "WARNING" in output

    def test_setup_chief_judge_workflow_no_group(self):
        """When no Chief Judge Moderator group, logs warning and returns."""
        from wagtail.models import Collection, Workflow, GroupApprovalTask, WorkflowTask

        if not Collection.objects.exists():
            Collection.add_root(name="Root")
        from home.management.commands.setup_wagtail_roles import Command

        cmd = Command.__new__(Command)
        out = StringIO()
        cmd.stdout = out
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        cmd.style.WARNING = lambda x: x

        task = GroupApprovalTask.objects.first()
        if not task:
            task = GroupApprovalTask.objects.create(name="Test Task 2")
        workflow, _ = Workflow.objects.get_or_create(name="Moderators approval")
        if not WorkflowTask.objects.filter(workflow=workflow).exists():
            WorkflowTask.objects.create(workflow=workflow, task=task, sort_order=1)

        Group.objects.filter(name="Chief Judge Moderator").delete()
        cmd.setup_chief_judge_workflow()

        output = out.getvalue()
        assert "Chief Judge Moderator" in output
        assert "not found" in output

    def test_setup_chief_judge_workflow_with_all_present(self):
        """When workflow and group both exist, runs successfully."""
        from wagtail.models import Collection, Workflow, GroupApprovalTask, WorkflowTask

        if not Collection.objects.exists():
            Collection.add_root(name="Root")
        from home.management.commands.setup_wagtail_roles import Command

        cmd = Command.__new__(Command)
        out = StringIO()
        cmd.stdout = out
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        cmd.style.WARNING = lambda x: x

        task = GroupApprovalTask.objects.first()
        if not task:
            task = GroupApprovalTask.objects.create(name="Test Task 3")
        workflow, _ = Workflow.objects.get_or_create(name="Moderators approval")
        if not WorkflowTask.objects.filter(workflow=workflow).exists():
            WorkflowTask.objects.create(workflow=workflow, task=task, sort_order=1)
        Group.objects.get_or_create(name="Chief Judge Moderator")

        cmd.setup_chief_judge_workflow()

        output = out.getvalue()
        assert "Chief Judge Moderator" in output
