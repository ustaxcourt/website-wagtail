"""Tests for home/models/snippets/faq_filter_tag.py and its delete protection."""

import pytest
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Locale, Page

from home.models import EnhancedStandardPage, FAQFilterTag
from home.models.snippets.faq_filter_tag import (
    get_faq_filter_tag_choices,
    get_filter_tag_usage,
)
from home.wagtail_hooks import (
    protect_filter_tags_in_use_from_deletion,
    protect_filter_tags_in_use_from_unpublish,
)

pytestmark = pytest.mark.django_db


def make_tag(name, live=True):
    tag = FAQFilterTag(name=name, live=live)
    tag.full_clean()
    tag.save()
    return tag


def make_page_with_qa(title, tag, question="How do I file?"):
    page = EnhancedStandardPage(
        title=title,
        slug=title.lower().replace(" ", "-"),
        body=[
            (
                "questionanswers",
                [
                    {
                        "question": question,
                        "answer": "<p>Answer</p>",
                        "anchortag": "1",
                        "filtertag": tag.slug,
                    }
                ],
            )
        ],
    )
    Locale.objects.get_or_create(language_code="en")
    root = Page.get_first_root_node() or Page.add_root(title="Root", slug="root")
    root.add_child(instance=page)
    return page


class TestValidation:
    def test_duplicate_name_rejected_case_insensitively(self):
        make_tag("Appeals")
        with pytest.raises(ValidationError) as exc:
            make_tag("aPPeals")
        assert "already exists" in str(exc.value)

    def test_edit_to_existing_name_rejected(self):
        make_tag("Appeals")
        other = make_tag("Motions")
        other.name = "APPEALS"
        with pytest.raises(ValidationError):
            other.full_clean()

    def test_resaving_same_name_allowed(self):
        tag = make_tag("Appeals")
        tag.name = "APPEALS"
        tag.full_clean()

    @pytest.mark.parametrize("name", ["All", "ALL", " all "])
    def test_all_is_reserved(self, name):
        with pytest.raises(ValidationError) as exc:
            make_tag(name)
        assert "All" in str(exc.value)

    def test_scheduled_expiry_rejected(self):
        tag = FAQFilterTag(name="Appeals", expire_at=timezone.now())
        with pytest.raises(ValidationError) as exc:
            tag.full_clean()
        assert "expire_at" in exc.value.message_dict


class TestSlugAndChoices:
    def test_slug_generated_and_unique(self):
        first = make_tag("Small Cases")
        assert first.slug == "small-cases"
        # Different name, same slugified value
        second = FAQFilterTag(name="Small-Cases!")
        second.full_clean()
        second.save()
        assert second.slug == "small-cases-2"

    def test_slug_stable_when_renamed(self):
        tag = make_tag("Small Cases")
        tag.name = "Simplified Cases"
        tag.save()
        tag.refresh_from_db()
        assert tag.slug == "small-cases"

    def test_choices_alphabetical_case_insensitive_and_live_only(self):
        make_tag("banana")
        make_tag("Cherry")
        make_tag("apple")
        make_tag("Hidden", live=False)
        assert [name for _, name in get_faq_filter_tag_choices()] == [
            "apple",
            "banana",
            "Cherry",
        ]


class TestUsageAndDeleteProtection:
    def test_usage_lists_the_qas_using_a_tag(self):
        tag = make_tag("Appeals")
        page = make_page_with_qa("Appeals FAQ", tag, question="Can I appeal?")
        make_page_with_qa("Other FAQ", make_tag("Filing"))
        assert [(p.pk, q) for p, q in get_filter_tag_usage(tag)] == [
            (page.pk, "Can I appeal?")
        ]

    def test_unused_tag_has_no_usage(self):
        assert get_filter_tag_usage(make_tag("Appeals")) == []

    def test_usage_found_in_latest_draft_revision(self):
        tag = make_tag("Appeals")
        page = make_page_with_qa("Appeals FAQ", make_tag("Filing"))
        draft = page.body.stream_block.to_python(
            [
                {
                    "type": "questionanswers",
                    "value": [
                        {
                            "question": "Draft only?",
                            "answer": "<p>x</p>",
                            "anchortag": "2",
                            "filtertag": tag.slug,
                        }
                    ],
                }
            ]
        )
        page.body = draft
        page.save_revision()
        page.refresh_from_db()
        # Live content does not use the tag, the draft does
        assert [q for _, q in get_filter_tag_usage(tag)] == ["Draft only?"]

    def _request(self):
        request = RequestFactory().post("/")
        request.session = {}
        request._messages = FallbackStorage(request)
        return request

    def test_hook_blocks_deletion_and_names_the_qas(self):
        tag = make_tag("Appeals")
        make_page_with_qa("Appeals FAQ", tag, question="Can I appeal?")
        request = self._request()
        response = protect_filter_tags_in_use_from_deletion(request, [tag])
        assert response.status_code == 302
        text = " ".join(str(m) for m in get_messages(request))
        assert "cannot be removed" in text
        assert "Can I appeal?" in text
        assert "Appeals FAQ" in text

    def test_hook_blocks_unpublish_and_names_the_qas(self):
        tag = make_tag("Appeals")
        make_page_with_qa("Appeals FAQ", tag, question="Can I appeal?")
        request = self._request()
        response = protect_filter_tags_in_use_from_unpublish(request, tag)
        assert response.status_code == 302
        text = " ".join(str(m) for m in get_messages(request))
        assert "cannot be unpublished" in text
        assert "Can I appeal?" in text

    def test_hook_allows_unpublish_of_unused_tag(self):
        request = self._request()
        tag = make_tag("Appeals")
        assert protect_filter_tags_in_use_from_unpublish(request, tag) is None

    def test_hook_allows_deletion_of_unused_tag(self):
        request = self._request()
        assert (
            protect_filter_tags_in_use_from_deletion(request, [make_tag("Appeals")])
            is None
        )
        assert list(get_messages(request)) == []


class TestAdminViews:
    @pytest.fixture
    def client(self, admin_client, settings):
        settings.GITHUB_SHA = "test1234567"
        return admin_client

    def test_add_view_rejects_duplicate_name(self, client):
        make_tag("Appeals")
        response = client.post(
            reverse("wagtailsnippets_home_faqfiltertag:add"), {"name": "APPEALS"}
        )
        assert response.status_code == 200
        assert "already exists" in response.content.decode()
        assert FAQFilterTag.objects.filter(name__iexact="appeals").count() == 1

    def test_delete_view_blocks_tag_in_use(self, client):
        tag = make_tag("Appeals")
        make_page_with_qa("Appeals FAQ", tag, question="Can I appeal?")
        url = reverse("wagtailsnippets_home_faqfiltertag:delete", args=[tag.pk])
        response = client.post(url, follow=True)
        assert FAQFilterTag.objects.filter(pk=tag.pk).exists()
        assert "Can I appeal?" in response.content.decode()

    def test_unpublish_view_blocks_tag_in_use(self, client):
        tag = make_tag("Appeals")
        make_page_with_qa("Appeals FAQ", tag, question="Can I appeal?")
        url = reverse("wagtailsnippets_home_faqfiltertag:unpublish", args=[tag.pk])
        response = client.post(url, follow=True)
        tag.refresh_from_db()
        assert tag.live
        assert "Can I appeal?" in response.content.decode()

    def test_unpublish_confirm_page_blocks_tag_in_use_up_front(self, client):
        tag = make_tag("Appeals")
        make_page_with_qa("Appeals FAQ", tag, question="Can I appeal?")
        url = reverse("wagtailsnippets_home_faqfiltertag:unpublish", args=[tag.pk])
        response = client.get(url, follow=True)
        body = response.content.decode()
        assert "cannot be unpublished" in body
        assert "Can I appeal?" in body
        assert "Yes, unpublish it" not in body

    def test_unpublish_confirm_page_shown_for_unused_tag(self, client):
        tag = make_tag("Appeals")
        url = reverse("wagtailsnippets_home_faqfiltertag:unpublish", args=[tag.pk])
        assert "Yes, unpublish it" in client.get(url).content.decode()

    def test_unpublish_view_allows_unused_tag(self, client):
        tag = make_tag("Appeals")
        url = reverse("wagtailsnippets_home_faqfiltertag:unpublish", args=[tag.pk])
        client.post(url)
        tag.refresh_from_db()
        assert not tag.live

    def test_delete_view_removes_unused_tag(self, client):
        tag = make_tag("Appeals")
        url = reverse("wagtailsnippets_home_faqfiltertag:delete", args=[tag.pk])
        client.post(url)
        assert not FAQFilterTag.objects.filter(pk=tag.pk).exists()
