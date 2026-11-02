import re
from taggit.models import Tag
from home.models import NavigationRibbon, SimpleCard, SimpleCardGroup, DawsonPage
from django.test import TestCase, RequestFactory
from wagtail.models import Locale, Page, Site, Collection
from home.management.commands.pages.efiling_and_case_maintenance.definitions_page import (
    DefinitionsPageInitializer,
)
from home.management.commands.pages.rules_and_guidance.guidence_for_petitioners import (
    GuidenceForPetitionersPageInitializer,
)


class TestDefinitionsPageInitializer(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        Locale.objects.get_or_create(language_code="en")

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            root_page = Page.add_root(title="Root", slug="root")

        home_page = Page(title="Home", slug="home")
        root_page.add_child(instance=home_page)

        Site.objects.get_or_create(
            hostname="localhost",
            defaults={"root_page": home_page, "is_default_site": True},
        )

        Collection.add_root(name="Root")
        NavigationRibbon.objects.create(name="Guidance for Petitioners Ribbon")
        dawson_page = DawsonPage(
            title="DAWSON",
            slug="dawson",
            search_description="Dawson eFiling main page",
            body="Placeholder body text.",
        )
        home_page.add_child(instance=dawson_page)
        dawson_card_group = SimpleCardGroup(
            group_label="Filing a Petition", parent_page=dawson_page
        )
        dawson_card_group.save()
        reference_materials_card = SimpleCard(
            card_title="Reference Materials",
            card_icon="book",
            parent_page=dawson_card_group,
        )
        reference_materials_card.save()
        glossary_page = Page(slug="petitioners-glossary", title="Petitioners Glossary")
        home_page.add_child(instance=glossary_page)

        TAGS_AND_COLLECTION_NAMES = [
            "Administrative Orders",
            "Cases Commenced in the Court of Appeals",
            "Citation and Style Manual",
            "Clinics",
            "DAWSON Training Guides",
            "Directory",
            "Discipline",
            "Engagement & Outreach",
            "Events and Webinars",
            "Fees & Charges",
            "Forms",
            "Guidance for Petitioners",
            "Guidance for Practitioners",
            "History",
            "Internship Programs",
            "Judges & Bios",
            "Judicial Conduct and Disability Procedures",
            "Law Clerk Programs",
            "LITC",
            "Mission Statement",
            "Pamphlets",
            "Press Releases",
            "Pro Bono Programs",
            "Records (Transcripts & Copies)",
            "DAWSON Release Notes",
            "Remote Proceedings",
            "Reports & Statistics",
            "Rules Comments and Suggestions",
            "Tax Court Reports",
            "Tax Court Rules",
            "Trial Sessions",
            "Vacancy Announcements",
        ]

        ROLE_TAGS_NAMES = [
            "Role Content Manager",
            "Role Website Manager",
            "Role Chief Judge",
            "Role Dawson Contributor",
            "Role Public Affairs",
            "Role Clerk Office",
            "Role Hr Committee",
            "Role Pro Se Committee",
            "Role Rules Committee",
            "Role Admissions Committee",
            "Role Ethics Committee",
            "Role Disciplinary Committee",
            "Role Reporters Office",
            "Role Appellate Reports",
            "Role Case Services",
        ]

        for tag_name in TAGS_AND_COLLECTION_NAMES:
            slug = re.sub(r"\s+", "-", tag_name.lower())
            # Use the slug to check for existence, and provide the name as a default
            # for creation. This avoids the unique constraint error.
            Tag.objects.get_or_create(slug=slug, defaults={"name": tag_name})

        for tag_name in ROLE_TAGS_NAMES:
            slug = re.sub(r"\s+", "-", tag_name.lower())
            # Use the slug to check for existence, and provide the name as a default
            # for creation. This avoids the unique constraint error.
            Tag.objects.get_or_create(slug=slug, defaults={"name": tag_name})

    def test_definitions_page_creates(self):
        initializer = DefinitionsPageInitializer()
        initializer.create()

        assert Page.objects.filter(slug="definitions").exists()

    def test_definitions_page_runs(self):
        initializer = DefinitionsPageInitializer()
        initializer.run()

        assert Page.objects.filter(slug="definitions").exists()

    def test_definitions_page_runs_with_petitioners_page_existing(self):
        petitioners_page_initializer = GuidenceForPetitionersPageInitializer()
        petitioners_page_initializer.create()

        initializer = DefinitionsPageInitializer()
        initializer.run()

        assert Page.objects.filter(slug="definitions").exists()
