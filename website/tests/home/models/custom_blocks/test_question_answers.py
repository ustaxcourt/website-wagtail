"""Tests for home/models/custom_blocks/question_answers.py and its FAQ rendering."""

import importlib
import re

import pytest
from django.test import RequestFactory
from wagtail.models import Locale, Page, Site

from home.management.commands.pages.rules_and_guidance.petitioners_help import (
    PLACEHOLDER_QUESTIONS,
    PetitionersHelpPageInitializer,
)
from home.models import EnhancedStandardPage, FAQFilterTag
from home.models.custom_blocks.question_answers import QuestionAnswersBlock

data_migration = importlib.import_module(
    "home.migrations.0157_data_wrap_questionanswers_pe"
)

pytestmark = pytest.mark.django_db


def make_tag(name, slug=None):
    tag = FAQFilterTag(name=name, live=True)
    if slug:
        tag.slug = slug
    tag.save()
    return tag


def qa(question, filtertag, anchortag=None):
    return {
        "question": question,
        "answer": f"<p>Answer to {question}</p>",
        "anchortag": anchortag or question.lower().replace(" ", "-").strip("?"),
        "filtertag": filtertag,
    }


def make_value(questions, display_filter_section=True):
    return QuestionAnswersBlock().to_python(
        {"display_filter_section": display_filter_section, "questions": questions}
    )


class TestQuestionAnswersValue:
    def test_filter_tags_follow_first_appearance_order(self):
        filing = make_tag("Filing")
        appeals = make_tag("Appeals")
        value = make_value(
            [
                qa("Q1", appeals.slug),
                qa("Q2", filing.slug),
                qa("Q3", appeals.slug),
            ]
        )
        assert value.filter_tags == [(appeals.slug, "Appeals"), (filing.slug, "Filing")]

    def test_filter_tags_skip_unknown_slugs(self):
        filing = make_tag("Filing")
        value = make_value([qa("Q1", "deleted-tag"), qa("Q2", filing.slug)])
        assert value.filter_tags == [(filing.slug, "Filing")]

    def test_entries_pair_each_question_with_its_tag_name(self):
        filing = make_tag("Filing")
        value = make_value([qa("Q1", filing.slug), qa("Q2", "deleted-tag")])
        assert [(item["question"], name) for item, name in value.entries] == [
            ("Q1", "Filing"),
            ("Q2", ""),
        ]

    def test_display_filter_section_defaults_to_false(self):
        assert QuestionAnswersBlock().get_default()["display_filter_section"] is False


class TestDataMigration:
    def test_wraps_top_level_and_nested_qa_lists(self):
        questions = [qa("Q1", "filing")]
        body = [
            {"type": "questionanswers", "value": list(questions)},
            {
                "type": "anchor_page",
                "value": {
                    "body": [{"type": "questionanswers", "value": list(questions)}]
                },
            },
        ]
        wrapped, changed = data_migration.wrap_qa_blocks(body)
        assert changed
        expected = {"display_filter_section": False, "questions": questions}
        assert wrapped[0]["value"] == expected
        assert wrapped[1]["value"]["body"][0]["value"] == expected

    def test_wrap_is_idempotent(self):
        body = [{"type": "questionanswers", "value": [qa("Q1", "filing")]}]
        once, _ = data_migration.wrap_qa_blocks(body)
        twice, changed = data_migration.wrap_qa_blocks(once)
        assert not changed
        assert twice == once

    def test_unwrap_restores_the_original_list(self):
        questions = [qa("Q1", "filing")]
        body = [{"type": "questionanswers", "value": list(questions)}]
        wrapped, _ = data_migration.wrap_qa_blocks(body)
        unwrapped, changed = data_migration.unwrap_qa_blocks(wrapped)
        assert changed
        assert unwrapped == [{"type": "questionanswers", "value": questions}]


class TestPetitionersHelpSeeder:
    def test_body_enables_filter_and_uses_only_existing_tags(self):
        seeded = {slug for slug, _, _ in PLACEHOLDER_QUESTIONS}
        missing = "after-decision"
        for slug in seeded - {missing}:
            make_tag(slug.replace("-", " ").title(), slug=slug)

        [block] = PetitionersHelpPageInitializer().build_body()

        value = block["value"]
        assert value["display_filter_section"] is True
        used = [item["filtertag"] for item in value["questions"]]
        assert set(used) == seeded - {missing}
        assert len(used) > len(set(used)), "some tags should be shared"


class TestRender:
    @pytest.fixture(autouse=True)
    def _static_settings(self, settings):
        settings.GITHUB_SHA = "test1234567"
        settings.STORAGES = {
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }

    def render(self, display_filter_section):
        Locale.objects.get_or_create(language_code="en")
        root = Page.get_first_root_node() or Page.add_root(title="Root", slug="root")
        home = root.add_child(instance=Page(title="Home", slug="home-faq-test"))
        Site.objects.get_or_create(
            hostname="localhost", defaults={"root_page": home, "is_default_site": True}
        )
        filing = make_tag("Filing")
        appeals = make_tag("Appeals")
        page = EnhancedStandardPage(
            title="FAQ",
            slug="faq",
            body=[
                {
                    "type": "questionanswers",
                    "value": {
                        "display_filter_section": display_filter_section,
                        "questions": [
                            qa("How do I file", filing.slug, anchortag="file"),
                            qa("Can I appeal", appeals.slug, anchortag="appeal"),
                        ],
                    },
                }
            ],
        )
        home.add_child(instance=page)
        request = RequestFactory().get(page.url)
        request.site = Site.objects.get(is_default_site=True)
        return page.serve(request).render().content.decode()

    def test_filter_section_renders_all_first_then_tags_in_order(self):
        html = self.render(display_filter_section=True)
        assert "data-faq" in html
        labels = ['class="faq__filter-label">All<', ">Filing<", ">Appeals<"]
        positions = [html.index(label) for label in labels]
        assert positions == sorted(positions)

    def test_filter_section_renders_collapsed_linked_questions(self):
        html = self.render(display_filter_section=True)
        assert 'id="file"' in html
        assert 'href="#file"' in html
        assert "Answer to How do I file" in html

    def test_filter_section_question_link_is_the_accessible_toggle(self):
        """The link carries the expanded state; the chevron isn't a second control."""
        html = self.render(display_filter_section=True)
        link = re.search(r'<a href="#file"[^>]*>', html).group(0)
        assert 'aria-expanded="false"' in link
        answer_id = re.search(r'aria-controls="([^"]+)"', link).group(1)
        assert f'id="{answer_id}"' in html
        faq_list = html.split('class="faq__list"', 1)[1].split("</ul>", 1)[0]
        assert "<button" not in faq_list

    def test_without_filter_section_renders_original_layout(self):
        html = self.render(display_filter_section=False)
        assert "data-faq" not in html
        assert "question-answer-block" in html
        assert "How do I file" in html
