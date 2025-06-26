"""
Management command to set up snippet moderation workflow and permissions.
Configures permissions for Editor and Moderator groups and assigns snippets to workflow.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Workflow, WorkflowContentType
from home.models import (
    CommonText,
    JudgeProfile,
    JudgeCollection,
    JudgeRole,
    NavigationRibbon,
    NavigationMenu,
)
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sets up snippet moderation workflow and permissions for Editor and Moderator groups"

    def add_arguments(self, parser):
        parser.add_argument(
            "workflow_name",
            type=str,
            help="Name of the workflow to assign snippets to",
        )

    def handle(self, *args, **options):
        workflow_name = options["workflow_name"]

        # List of snippet models
        snippet_models = [
            CommonText,
            JudgeProfile,
            JudgeCollection,
            JudgeRole,
            NavigationRibbon,
            NavigationMenu,
        ]

        self.stdout.write(
            self.style.SUCCESS(
                f"SETTING UP SNIPPET MODERATION FOR WORKFLOW: {workflow_name}"
            )
        )

        # Always run both operations
        self.handle_permissions(snippet_models)
        self.stdout.write("\n" + "=" * 70)
        self.handle_workflow(workflow_name, snippet_models)

    def handle_permissions(self, snippet_models):
        """Handle granting permissions to Editor and Moderator groups."""

        self.stdout.write(
            self.style.SUCCESS("MANAGING PERMISSIONS FOR EDITOR AND MODERATOR GROUPS")
        )

        # Define groups and their permissions
        group_configs = {
            "Editors": [
                "view",  # View snippets in admin
                "add",  # Create new snippets
                "change",  # Edit existing snippets
                "delete",  # Delete snippets
            ],
            "Moderators": [
                "view",  # View snippets in admin
                "add",  # Create new snippets
                "change",  # Edit existing snippets
                "delete",  # Delete snippets
                "publish",  # Publish/approve snippets
            ],
        }

        for group_name, permissions_to_grant in group_configs.items():
            self.stdout.write(f"\n--- Processing {group_name} group ---")

            # Get the group
            try:
                group = Group.objects.get(name=group_name)
                self.stdout.write(self.style.SUCCESS(f"Found group: '{group.name}'"))
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Group '{group_name}' not found - skipping")
                )
                continue

            # Get current permissions
            current_permissions = set(group.permissions.all())
            current_permission_names = [p.codename for p in current_permissions]

            self.stdout.write(
                f"Current permissions for {group_name}: {len(current_permission_names)} permissions"
            )

            # Process each snippet model
            granted_count = 0
            already_granted_count = 0

            for model in snippet_models:
                content_type = ContentType.objects.get_for_model(model)
                model_name = model.__name__

                self.stdout.write(f"\nProcessing {model_name} for {group_name}:")

                for perm_type in permissions_to_grant:
                    perm_codename = f"{perm_type}_{model._meta.model_name}"

                    try:
                        permission = Permission.objects.get(
                            content_type=content_type, codename=perm_codename
                        )

                        if permission in current_permissions:
                            self.stdout.write(
                                self.style.WARNING(f"  {perm_codename} already granted")
                            )
                            already_granted_count += 1
                        else:
                            group.permissions.add(permission)
                            self.stdout.write(
                                self.style.SUCCESS(f"  Granted {perm_codename}")
                            )
                            granted_count += 1

                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f"  Permission {perm_codename} not found")
                        )

            # Summary for this group
            self.stdout.write(f"\n{group_name} Summary:")
            self.stdout.write(f"  Granted {granted_count} new permissions")
            self.stdout.write(f"  Already had {already_granted_count} permissions")

            # Show final state for this group
            group.refresh_from_db()
            final_permissions = group.permissions.all()
            snippet_permissions = [
                p.codename
                for p in final_permissions
                if any(model._meta.model_name in p.codename for model in snippet_models)
            ]
            self.stdout.write(
                f"  Total snippet permissions: {len(snippet_permissions)}"
            )

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS("PERMISSION SETUP COMPLETE FOR BOTH GROUPS")
        )

    def handle_workflow(self, workflow_name, snippet_models):
        """Handle assigning snippets to workflow."""

        self.stdout.write(
            self.style.SUCCESS(f"MANAGING WORKFLOW ASSIGNMENTS: {workflow_name}")
        )

        # Get the workflow
        try:
            workflow = Workflow.objects.get(name=workflow_name)
            self.stdout.write(self.style.SUCCESS(f"Found workflow: '{workflow.name}'"))
        except Workflow.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Workflow '{workflow_name}' not found"))
            return

        # Get current assignments
        current_workflow_content_types = workflow.workflow_content_types.all()
        current_content_types = set(
            [wct.content_type for wct in current_workflow_content_types]
        )
        current_model_names = [
            wct.content_type.model_class().__name__
            for wct in current_workflow_content_types
        ]

        self.stdout.write(f"Currently assigned content types: {current_model_names}")

        # Process each snippet model
        assigned_count = 0
        already_assigned_count = 0

        for model in snippet_models:
            content_type = ContentType.objects.get_for_model(model)
            model_name = model.__name__

            if content_type in current_content_types:
                self.stdout.write(
                    self.style.WARNING(
                        f"  {model_name} is already assigned to this workflow"
                    )
                )
                already_assigned_count += 1
            else:
                WorkflowContentType.objects.create(
                    workflow=workflow, content_type=content_type
                )
                self.stdout.write(
                    self.style.SUCCESS(f"  Assigned {model_name} to workflow")
                )
                assigned_count += 1

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"WORKFLOW ASSIGNMENT COMPLETE: Assigned {assigned_count} new content types"
            )
        )

        self.stdout.write(f"Already assigned: {already_assigned_count}")
        self.stdout.write(f"Total snippet models: {len(snippet_models)}")

        # Show final state
        workflow.refresh_from_db()
        final_workflow_content_types = workflow.workflow_content_types.all()
        final_model_names = [
            wct.content_type.model_class().__name__
            for wct in final_workflow_content_types
        ]
        self.stdout.write(f"Final assigned content types: {final_model_names}")

        # Final summary
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("SNIPPET MODERATION SETUP COMPLETE!"))
        self.stdout.write("Configuration Summary:")
        self.stdout.write(f"  - Workflow: {workflow_name}")
        self.stdout.write(
            "  - Editors: Can view, create, update, delete snippets (all actions go through moderation)"
        )
        self.stdout.write(
            "  - Moderators: Full access including publish/approve capabilities"
        )
        self.stdout.write(f"  - Snippet models configured: {len(snippet_models)}")
        self.stdout.write(
            "  - Users need to log out and log back in to see snippet menu"
        )
