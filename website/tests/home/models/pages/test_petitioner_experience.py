from unittest.mock import PropertyMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db import models
from wagtail import blocks
from wagtail.models import Page

from home.models.pages.petitioner_experience import (
    PageSelectorBlock,
    PetitionerExperiencePage,
    PetitionerExperienceReviewByRequiredOnSubmitForm,
)


class PetitionerExperienceTestForm(PetitionerExperienceReviewByRequiredOnSubmitForm):
    class Meta:
        model = PetitionerExperiencePage
        fields = ("slug", "navigation_ribbon")


def make_page(breadcrumb_title="", page_block=None):
    page = PetitionerExperiencePage.__new__(PetitionerExperiencePage)
    models.Model.__init__(page)
    page.navigation_ribbon_id = 1
    page.breadcrumb = []
    if breadcrumb_title or page_block:
        breadcrumb_field = PetitionerExperiencePage._meta.get_field("breadcrumb")
        page.breadcrumb = breadcrumb_field.to_python(
            [
                {
                    "type": "breadcrumb",
                    "value": {
                        "breadcrumb_title": breadcrumb_title,
                        "breadcrumb_page": (
                            [{"type": page_block[0], "value": page_block[1]}]
                            if page_block
                            else []
                        ),
                    },
                },
            ]
        )
    return page


@pytest.mark.parametrize(
    "breadcrumb_title,page_block,error_message",
    [
        (
            "Petitioner Experience",
            None,
            "A Breadcrumb Page must be provided when Breadcrumb Title is provided.",
        ),
        (
            "",
            ("external_url", "https://example.com/"),
            "A Breadcrumb Title must be provided when Breadcrumb Page is provided.",
        ),
    ],
)
def test_breadcrumb_fields_must_be_provided_together(
    breadcrumb_title, page_block, error_message
):
    page = make_page(breadcrumb_title, page_block)

    with patch("home.models.pages.petitioner_experience.EnhancedStandardPage.clean"):
        with pytest.raises(ValidationError) as error:
            page.clean()

    assert error_message in error.value.message_dict["breadcrumb"]


def test_breadcrumb_fields_may_both_be_empty():
    page = make_page()

    with patch("home.models.pages.petitioner_experience.EnhancedStandardPage.clean"):
        page.clean()


def test_page_selector_block_supports_internal_and_external_pages():
    child_blocks = PageSelectorBlock().child_blocks
    assert set(child_blocks) == {"internal_page", "external_url"}
    assert isinstance(child_blocks["internal_page"], blocks.PageChooserBlock)
    assert isinstance(child_blocks["external_url"], blocks.URLBlock)


@pytest.mark.parametrize(
    "instance_slug,submitted_slug,expected_required",
    [
        ("ordinary-page", "dawson-how-to-new-guide", False),
        ("dawson-how-to-old-guide", "ordinary-page", True),
    ],
)
@pytest.mark.django_db
def test_navigation_ribbon_requirement_uses_submitted_slug(
    instance_slug, submitted_slug, expected_required
):
    page = PetitionerExperiencePage(title="Test", slug=instance_slug)

    form = PetitionerExperienceTestForm(data={"slug": submitted_slug}, instance=page)

    assert form.fields["navigation_ribbon"].required is expected_required


@pytest.mark.parametrize(
    "slug,expected_required",
    [("ordinary-page", True), ("dawson-how-to-guide", False)],
)
@pytest.mark.django_db
def test_unbound_navigation_ribbon_requirement_uses_instance_slug(
    slug, expected_required
):
    page = PetitionerExperiencePage(title="Test", slug=slug)

    form = PetitionerExperienceTestForm(instance=page)

    assert form.fields["navigation_ribbon"].required is expected_required


def test_breadcrumb_uses_external_page_url():
    page = make_page("Petitioner Experience", ("external_url", "https://example.com/"))

    assert page.breadcrumb_title == "Petitioner Experience"
    assert page.breadcrumb_page_url == "https://example.com/"


def test_breadcrumb_uses_internal_page_url():
    page = make_page("Petitioner Experience", ("internal_page", 1))
    selected_page = Page(id=1)

    with (
        patch.object(Page.objects, "in_bulk", return_value={1: selected_page}),
        patch.object(
            Page, "url", new_callable=PropertyMock, return_value="/petitioners/"
        ),
    ):
        assert page.breadcrumb_page_url == "/petitioners/"
