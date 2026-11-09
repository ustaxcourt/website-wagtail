from unittest.mock import PropertyMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db import models
from wagtail import blocks
from wagtail.models import Page

from home.models.pages.petitioner_experience import (
    PageSelectorBlock,
    PetitionerExperiencePage,
)


class PetitionerExperienceTestForm(PetitionerExperiencePage.base_form_class):
    class Meta:
        model = PetitionerExperiencePage
        fields = ("slug", "navigation_ribbon")


def make_page(breadcrumb_title="", page_block=None):
    page = PetitionerExperiencePage.__new__(PetitionerExperiencePage)
    models.Model.__init__(page)
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


@pytest.mark.parametrize(
    "slug",
    ["ordinary-page", "dawson-how-to-guide", "dawson-troubleshoot-file-uploads"],
)
def test_navigation_ribbon_is_optional(slug):
    page = make_page()
    page.slug = slug
    assert page.navigation_ribbon_id is None

    with patch("home.models.pages.petitioner_experience.EnhancedStandardPage.clean"):
        page.clean()


def test_page_selector_block_supports_internal_and_external_pages():
    child_blocks = PageSelectorBlock().child_blocks
    assert set(child_blocks) == {"internal_page", "external_url"}
    assert isinstance(child_blocks["internal_page"], blocks.PageChooserBlock)
    assert isinstance(child_blocks["external_url"], blocks.URLBlock)
    breadcrumb = PetitionerExperiencePage._meta.get_field(
        "breadcrumb"
    ).stream_block.child_blocks["breadcrumb"]
    assert breadcrumb.child_blocks["breadcrumb_title"].required


@pytest.mark.parametrize(
    "instance_slug,submitted_slug",
    [
        ("ordinary-page", "dawson-how-to-new-guide"),
        ("dawson-how-to-old-guide", "ordinary-page"),
        ("ordinary-page", "dawson-troubleshoot-file-uploads"),
    ],
)
@pytest.mark.django_db
def test_navigation_ribbon_is_optional_regardless_of_submitted_slug(
    instance_slug, submitted_slug
):
    page = PetitionerExperiencePage(title="Test", slug=instance_slug)

    form = PetitionerExperienceTestForm(data={"slug": submitted_slug}, instance=page)

    assert not form.fields["navigation_ribbon"].required


@pytest.mark.parametrize(
    "slug",
    ["ordinary-page", "dawson-how-to-guide", "dawson-troubleshoot-file-uploads"],
)
@pytest.mark.django_db
def test_unbound_navigation_ribbon_is_optional_regardless_of_instance_slug(slug):
    page = PetitionerExperiencePage(title="Test", slug=slug)

    form = PetitionerExperienceTestForm(instance=page)

    assert not form.fields["navigation_ribbon"].required


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
