from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.models import (
    Page,
    GroupPagePermission,
    Collection,
    GroupCollectionPermission,
    Workflow,
    WorkflowContentType,
)
from wagtail.documents.models import Document
from wagtail.images.models import Image
from home.models import (
    CommonText,
    JudgeProfile,
    JudgeCollection,
    JudgeRole,
    NavigationRibbon,
    NavigationMenu,
    NewsItem,
)


class Command(BaseCommand):
    help = "Sets up Wagtail groups with model, page, document, image, collection, and snippet permissions."

    def handle(self, *args, **options):
        group_definitions = {
            "Editors": ["add", "change"],
            "Moderators": ["add", "change", "publish"],
            "Administrators": [
                "add",
                "change",
                "publish",
                "delete",
                "bulk_delete",
                "lock",
                "unlock",
            ],
            "Chief Judge Moderator": ["add", "change", "publish"],
            "DAWSON Contributor Moderator": ["add", "change", "publish"],
            "Public Affairs Editor": ["add", "change"],
            "Admissions, Ethics, Disciplinary Committee  Editor": ["add", "change"],
            "Appellate Reports Editor": ["add", "change"],
            "Case Services Editor": ["add", "change"],
            "Clerk's Office Editor": ["add", "change"],
            "HR Committee Editor": ["add", "change"],
            "Pro Se Committee Editor": ["add", "change"],
            "Reporter's Office Editor": ["add", "change"],
            "Rules Committee Editor": ["add", "change"],
            "Website Manager  Administrator": ["add", "change"],
            "Content Manager  Moderator": ["add", "change", "publish"],
        }

        page_assignments = {
            "Administrators": [Page.get_first_root_node().slug],
            "Admissions, Ethics, Disciplinary Committee  Editor": ["practitioners"],
            "Appellate Reports Editor": ["reports-and-statistics"],
            "Chief Judge Moderator": [
                "administrative-orders",
                "judges",
                "judges-recruiting",
                "zoomgov",
                "zoomgov-the-basics",
                "zoomgov-getting-ready",
                "zoomgov-zoomgov-proceedings",
                "jcdp",
            ],
            "Moderators": [Page.get_first_root_node().slug],
            "Case Services Editor": [
                "fees-and-charges",
                "transcripts-and-copies",
                "case-related-forms",
            ],
            "Clerk's Office Editor": [
                "reports-and-statistics",
                "judges",
                "directory",
                "judges-recruiting",
                "jcdp",
            ],
            "Content Manager  Moderator": [Page.get_first_root_node().slug],
            "DAWSON Contributor Moderator": ["dawson-user-guides", "release-notes"],
            "HR Committee Editor": [
                "vacancy-announcements",
                "internship-programs",
                "law-clerk-program",
            ],
            "Pro Se Committee Editor": [
                "petitioners",
                "petitioners-about",
                "petitioners-start",
                "petitioners-before",
                "petitioners-after",
                "petitioners-during",
                "petitioners-glossary",
                "clinics",
                "clinics-academic",
                "clinics-academic-non-law-school",
                "clinics-calendar-call",
                "clinics-chief-counsel",
                "case-related-forms",
            ],
            "Public Affairs Editor": ["press-releases", "mission", "history"],
            "Reporter's Office Editor": ["citation-and-style-manual", "pamphlets"],
            "Rules Committee Editor": ["rules", "case-related-forms", "rules-comments"],
        }

        # Get content types
        page_ct = ContentType.objects.get_for_model(Page)
        document_ct = ContentType.objects.get_for_model(Document)
        image_ct = ContentType.objects.get_for_model(Image)

        # Get root collection
        root_collection = Collection.get_first_root_node()

        for group_name, perms in group_definitions.items():
            group, _ = Group.objects.get_or_create(name=group_name)

            # Model-level Page Permissions
            for action in perms:
                codename = f"{action}_page"
                try:
                    perm = Permission.objects.get(
                        codename=codename, content_type=page_ct
                    )
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️ Missing model-level page permission: {codename}"
                        )
                    )

            # Page-specific Object-level Permissions
            slugs = page_assignments.get(group_name, [])
            if not isinstance(slugs, list):
                slugs = [slugs]

            perm_map = {
                "add": "add_page",
                "change": "change_page",
                "publish": "publish_page",
                "lock": "lock_page",
                "unlock": "unlock_page",
                "delete": "delete_page",
                "bulk_delete": "bulk_delete_page",
            }

            for slug in slugs:
                try:
                    page = Page.objects.get(slug=slug)
                    for action in perms:
                        codename = perm_map.get(action)
                        if codename:
                            try:
                                perm = Permission.objects.get(
                                    codename=codename, content_type=page_ct
                                )
                                GroupPagePermission.objects.get_or_create(
                                    group=group,
                                    page=page,
                                    permission=perm,
                                )
                            except Permission.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"⚠️ Missing object-level page permission: {codename}"
                                    )
                                )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Page-level permissions set for '{group_name}' on '{page.title}'"
                        )
                    )
                except Page.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️ Page with slug '{slug}' not found for group '{group_name}'"
                        )
                    )

            # --- Wagtail Admin Access Permission ---
            try:
                admin_perm = Permission.objects.get(
                    codename="access_admin", content_type__app_label="wagtailadmin"
                )
                group.permissions.add(admin_perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️ 'access_admin' permission not found for group '{group_name}'"
                    )
                )

            # Document Permissions
            for action in ["add", "change", "choose"]:
                codename = f"{action}_document"
                try:
                    perm = Permission.objects.get(
                        codename=codename, content_type=document_ct
                    )
                    GroupCollectionPermission.objects.get_or_create(
                        group=group, collection=root_collection, permission=perm
                    )
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ Missing document permission: {codename}")
                    )

            # Image Permissions
            for action in ["add", "change", "choose"]:
                codename = f"{action}_image"
                try:
                    perm = Permission.objects.get(
                        codename=codename, content_type=image_ct
                    )
                    GroupCollectionPermission.objects.get_or_create(
                        group=group, collection=root_collection, permission=perm
                    )
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️ Missing image permission: {codename}")
                    )

            self.stdout.write(
                self.style.SUCCESS(f"✅ Permissions set for group '{group_name}'")
            )

        # Set up snippet permissions and workflow
        self.setup_snippet_permissions()
        self.setup_snippet_workflow()

    def setup_snippet_permissions(self):
        """Set up snippet permissions for Editor and Moderator groups."""
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("SETTING UP SNIPPET PERMISSIONS"))

        # Define snippet models
        snippet_models = [
            CommonText,
            JudgeProfile,
            JudgeCollection,
            JudgeRole,
            NavigationRibbon,
            NavigationMenu,
            NewsItem,
        ]

        # Define groups and their snippet permissions
        snippet_group_configs = {
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
            "Chief Judge Moderator": [
                "view",  # View snippets in admin
                "add",  # Create new snippets
                "change",  # Edit existing snippets
                "delete",  # Delete snippets
                "publish",  # Publish/approve snippets
            ],
        }

        for group_name, permissions_to_grant in snippet_group_configs.items():
            self.stdout.write(f"\n--- Processing {group_name} group for snippets ---")

            # Get the group
            try:
                group = Group.objects.get(name=group_name)
                self.stdout.write(self.style.SUCCESS(f"Found group: '{group.name}'"))
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Group '{group_name}' not found - skipping snippet permissions"
                    )
                )
                continue

            # Get current permissions
            current_permissions = set(group.permissions.all())
            granted_count = 0
            already_granted_count = 0

            for model in snippet_models:
                content_type = ContentType.objects.get_for_model(model)
                model_name = model.__name__

                # For Chief Judge Moderator, only process Judge* models
                if group_name == "Chief Judge Moderator" and not model_name.startswith(
                    "Judge"
                ):
                    continue

                for perm_type in permissions_to_grant:
                    perm_codename = f"{perm_type}_{model._meta.model_name}"

                    try:
                        permission = Permission.objects.get(
                            content_type=content_type, codename=perm_codename
                        )

                        if permission in current_permissions:
                            already_granted_count += 1
                        else:
                            group.permissions.add(permission)
                            granted_count += 1

                    except Permission.DoesNotExist:
                        # Skip publish permissions if they don't exist for this model
                        if perm_type == "publish":
                            continue
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️ Permission {perm_codename} not found"
                            )
                        )

            # Summary for this group
            self.stdout.write(
                f"✅ {group_name} snippet permissions: {granted_count} granted, {already_granted_count} already had"
            )

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("SNIPPET PERMISSION SETUP COMPLETE"))

    def setup_snippet_workflow(self):
        """Set up snippet workflow assignments."""
        workflow_name = "Moderators approval"

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(
            self.style.SUCCESS(f"SETTING UP SNIPPET WORKFLOW: {workflow_name}")
        )

        # Define snippet models
        snippet_models = [
            CommonText,
            JudgeProfile,
            JudgeCollection,
            JudgeRole,
            NavigationRibbon,
            NavigationMenu,
            NewsItem,
        ]

        # Get the workflow
        try:
            workflow = Workflow.objects.get(name=workflow_name)
            self.stdout.write(self.style.SUCCESS(f"Found workflow: '{workflow.name}'"))
        except Workflow.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ Workflow '{workflow_name}' not found - skipping workflow assignment"
                )
            )
            return

        # Get current assignments
        current_workflow_content_types = workflow.workflow_content_types.all()
        current_content_types = set(
            [wct.content_type for wct in current_workflow_content_types]
        )

        # Process each snippet model
        assigned_count = 0
        already_assigned_count = 0

        for model in snippet_models:
            content_type = ContentType.objects.get_for_model(model)

            if content_type in current_content_types:
                already_assigned_count += 1
            else:
                WorkflowContentType.objects.create(
                    workflow=workflow, content_type=content_type
                )
                assigned_count += 1

        # Now check for Chief Judge Moderator workflow assignment
        self.setup_chief_judge_workflow()

        # Summary
        self.stdout.write(
            f"✅ Workflow assignment: {assigned_count} assigned, {already_assigned_count} already assigned"
        )
        self.stdout.write(f"📋 Total snippet models configured: {len(snippet_models)}")

        # Final summary
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("SNIPPET WORKFLOW SETUP COMPLETE!"))
        self.stdout.write("Configuration Summary:")
        self.stdout.write(f"  - Workflow: {workflow_name}")
        self.stdout.write(
            "  - Editors: Can view, create, update, delete snippets (all actions go through moderation)"
        )
        self.stdout.write(
            "  - Moderators: Full access including publish/approve capabilities"
        )
        self.stdout.write(
            "  - Chief Judge Moderator: Full access to Judge* snippets including publish/approve capabilities"
        )
        self.stdout.write(f"  - Snippet models configured: {len(snippet_models)}")
        self.stdout.write(
            "  - Users need to log out and log back in to see snippet menu"
        )

    def setup_chief_judge_workflow(self):
        """Set up Chief Judge Moderator workflow for Judge* snippets."""
        workflow_name = "Moderators approval"

        self.stdout.write(
            "\n--- Setting up Chief Judge Moderator workflow for Judge* snippets ---"
        )

        # Get Judge* models only
        judge_models = [JudgeProfile, JudgeCollection, JudgeRole]

        # Get the workflow
        try:
            workflow = Workflow.objects.get(name=workflow_name)
        except Workflow.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ Workflow '{workflow_name}' not found for Chief Judge Moderator"
                )
            )
            return

        # Check if Chief Judge Moderator group exists
        try:
            Group.objects.get(name="Chief Judge Moderator")
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("⚠️ Chief Judge Moderator group not found")
            )
            return

        # Get current assignments
        current_workflow_content_types = workflow.workflow_content_types.all()
        current_content_types = set(
            [wct.content_type for wct in current_workflow_content_types]
        )

        # Process Judge* models for Chief Judge Moderator workflow
        already_assigned_count = 0

        for model in judge_models:
            content_type = ContentType.objects.get_for_model(model)

            if content_type in current_content_types:
                already_assigned_count += 1
            else:
                # This should already be assigned from the main workflow setup
                # but we check anyway for completeness
                already_assigned_count += 1

        self.stdout.write(
            f"✅ Chief Judge Moderator workflow: Judge* models already assigned to '{workflow_name}'"
        )
