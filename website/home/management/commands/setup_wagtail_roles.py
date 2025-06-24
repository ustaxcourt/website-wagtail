from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.models import (
    Page,
    GroupPagePermission,
    Collection,
    GroupCollectionPermission,
)
from wagtail.documents.models import Document
from wagtail.images.models import Image


class Command(BaseCommand):
    help = "Sets up Wagtail groups with model, page, document, image, and collection permissions."

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
            "Chief Judge Moderator": [Page.get_first_root_node().slug],
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
