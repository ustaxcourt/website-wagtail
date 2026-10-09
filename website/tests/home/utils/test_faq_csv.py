"""Tests for home/utils/faq_csv.py and the FAQ CSV admin views."""

import csv
import io
import json
import re
from types import SimpleNamespace

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.urls import reverse
from wagtail.models import Locale, Page, Site

from home.models import EnhancedStandardPage, FAQFilterTag, ReleaseNotes
from home.utils.faq_csv import (
    FAQCSVError,
    faq_csv_parse,
    faq_section_import_csv,
    faq_section_to_csv,
    faq_sections_list,
)
from home.wagtail_hooks import faq_csv_page_header_button

pytestmark = pytest.mark.django_db


def make_tag(name, live=True):
    tag = FAQFilterTag(name=name, live=live)
    tag.save()
    return tag


def to_csv(rows):
    output = io.StringIO()
    csv.writer(output).writerows(rows)
    return output.getvalue().encode("utf-8")


def values(parsed):
    """Question dicts from parsed data, without the editor's generated block keys."""
    return [
        {**item["value"], "answer": strip_block_keys(item["value"]["answer"])}
        for item in parsed
    ]


def strip_block_keys(html):
    return re.sub(r' data-block-key="[^"]*"', "", html)


def errors_for(data, **kwargs):
    with pytest.raises(FAQCSVError) as excinfo:
        faq_csv_parse(data, **kwargs)
    return excinfo.value.errors


def qa(question, filtertag, anchortag):
    return {
        "question": question,
        "answer": f"<p>Answer to {question}</p>",
        "anchortag": anchortag,
        "filtertag": filtertag,
    }


@pytest.fixture
def filing():
    return make_tag("Filing")


@pytest.fixture
def page(filing):
    """A published page with one FAQ section, plus another nested in Card Tiles."""
    Locale.objects.get_or_create(language_code="en")
    root = Page.get_first_root_node() or Page.add_root(title="Root", slug="root")
    home = root.add_child(instance=Page(title="Home", slug="home-faq-csv-test"))
    Site.objects.get_or_create(
        hostname="localhost", defaults={"root_page": home, "is_default_site": True}
    )
    page = EnhancedStandardPage(
        title="FAQ",
        slug="faq",
        body=[
            {
                "type": "questionanswers",
                "id": "top-section",
                "value": {
                    "display_filter_section": True,
                    "questions": [qa("How do I file", filing.slug, "file")],
                },
            },
            {
                "type": "card_tiles",
                "value": {
                    "tiles": [],
                    "default_content": [
                        {
                            "type": "questionanswers",
                            "id": "nested-section",
                            "value": {
                                "display_filter_section": False,
                                "questions": [
                                    qa("Can I appeal", filing.slug, "appeal")
                                ],
                            },
                        }
                    ],
                },
            },
        ],
    )
    home.add_child(instance=page)
    page.save_revision().publish()
    return page


class TestFaqCsvParse:
    def test_maps_tag_names_case_insensitively_and_wraps_plain_text(self, filing):
        parsed = faq_csv_parse(
            to_csv(
                [
                    ["question", "answer", "filtertag", "anchortag"],
                    [
                        "How do I file?",
                        "Line one\nline two\n\nSecond",
                        "FILING",
                        "file",
                    ],
                ]
            )
        )
        assert values(parsed) == [
            {
                "question": "How do I file?",
                "answer": "<p>Line one<br/>line two</p><p>Second</p>",
                "anchortag": "file",
                "filtertag": filing.slug,
            }
        ]

    def test_accepts_spreadsheet_style_headers_and_a_byte_order_mark(self, filing):
        data = "﻿Question,Answer,Filter Tag,Anchor_Tag\nQ,A,Filing,a\n".encode("utf-8")
        assert values(faq_csv_parse(data))[0]["anchortag"] == "a"

    def test_reads_windows_1252_files(self, filing):
        data = "question,answer,filtertag\nCaf\xe9?,A,Filing\n".encode("cp1252")
        assert values(faq_csv_parse(data))[0]["question"] == "Caf\xe9?"

    def test_generates_unique_anchors_that_avoid_reserved_and_given_ones(self, filing):
        parsed = faq_csv_parse(
            to_csv(
                [
                    ["question", "answer", "filtertag", "anchortag"],
                    ["How do I file?", "A", "Filing", ""],
                    ["How do I file?", "A", "Filing", ""],
                    ["Other", "A", "Filing", "how-do-i-file-3"],
                ]
            ),
            reserved_anchors={"how-do-i-file"},
        )
        assert [v["anchortag"] for v in values(parsed)] == [
            "how-do-i-file-2",
            "how-do-i-file-4",
            "how-do-i-file-3",
        ]

    def test_anchortag_column_is_optional(self, filing):
        parsed = faq_csv_parse(
            to_csv([["question", "answer", "filtertag"], ["Q", "A", "Filing"]])
        )
        assert values(parsed)[0]["anchortag"] == "q"

    def test_skips_blank_rows(self, filing):
        parsed = faq_csv_parse(
            to_csv(
                [
                    ["question", "answer", "filtertag"],
                    ["", "", ""],
                    ["Q", "A", "Filing"],
                    ["  ", ""],
                ]
            )
        )
        assert len(parsed) == 1

    def test_keeps_links_and_drops_unsupported_html(self, filing):
        answer = '<p>See <a href="https://example.com">this</a>.<script>alert(1)</script></p>'
        parsed = faq_csv_parse(
            to_csv([["question", "answer", "filtertag"], ["Q", answer, "Filing"]])
        )
        html = values(parsed)[0]["answer"]
        assert '<a href="https://example.com">this</a>' in html
        assert "script" not in html

    def test_reports_every_row_problem_at_once(self, filing):
        make_tag("Draft tag", live=False)
        errors = errors_for(
            to_csv(
                [
                    ["question", "answer", "filtertag", "anchortag"],
                    ["Q1", "A", "Nope", "dup"],
                    ["Q2", "A", "Draft tag", "dup"],
                    ["Q3", "", "Filing", "taken"],
                    ["Q4", "A", "", ""],
                ]
            ),
            reserved_anchors={"taken"},
        )
        assert errors == [
            'Row 2: FilterTag "Nope" does not exist or is not published.',
            'Row 3: FilterTag "Draft tag" does not exist or is not published.',
            'Row 3: anchortag "dup" is already used on row 2.',
            'Row 4: anchortag "taken" is already used by another FAQ section on this page.',
            "Row 4: answer: This field is required.",
            "Row 5: FilterTag is required.",
        ]

    def test_tag_unpublished_mid_upload_is_a_row_error(self, filing, monkeypatch):
        # The tag lookup still sees "Filing", but the block's choices no longer do
        stale = FAQFilterTag(name="Unpublished", slug="unpublished")
        monkeypatch.setattr(
            "home.utils.faq_csv.FAQFilterTag",
            SimpleNamespace(objects=SimpleNamespace(filter=lambda **kwargs: [stale])),
        )
        errors = errors_for(
            to_csv([["question", "answer", "filtertag"], ["Q", "A", "Unpublished"]])
        )
        assert errors

    @pytest.mark.parametrize(
        "data, expected",
        [
            (b"", "The file is empty."),
            (b"question,answer,filtertag\n", "The file has no questions."),
            (
                b"question,answer,tag\n",
                'Unrecognized column(s): "tag". Expected columns: question, answer, filtertag, anchortag.',
            ),
            (b"question,answer\n", "Missing required column(s): filtertag."),
            (b"question,answer,filtertag,Answer\n", "Repeated column(s): answer."),
            (
                b"question,answer,filtertag\nQ,A,Filing,extra\n",
                "Row 2: has more values than there are columns.",
            ),
        ],
    )
    def test_rejects_malformed_files(self, filing, data, expected):
        assert expected in errors_for(data)


class TestFaqSectionToCsv:
    def test_round_trips_through_parse(self, page, filing):
        section = faq_sections_list(page)[0]
        text = faq_section_to_csv(section)
        assert text.splitlines() == [
            "question,answer,filtertag,anchortag",
            "How do I file,<p>Answer to How do I file</p>,Filing,file",
        ]
        assert values(faq_csv_parse(text.encode("utf-8"))) == values(
            section["value"]["questions"]
        )


class TestFaqSectionImportCsv:
    def request(self, admin_user):
        request = RequestFactory().post("/")
        request.user = admin_user
        return request

    def latest(self, page):
        return Page.objects.get(pk=page.pk).specific.get_latest_revision_as_object()

    def test_replace_saves_a_draft_and_keeps_section_settings(self, page, admin_user):
        data = to_csv(
            [["question", "answer", "filtertag"], ["New Q", "New A", "filing"]]
        )
        faq_section_import_csv(
            request=self.request(admin_user),
            page=page,
            data=data,
            section_id="top-section",
        )

        page.refresh_from_db()
        assert page.has_unpublished_changes
        live_section = faq_sections_list(page)[0]
        assert (
            live_section["value"]["questions"][0]["value"]["question"]
            == "How do I file"
        )

        draft_section = faq_sections_list(self.latest(page))[0]
        assert draft_section["id"] == "top-section"
        assert draft_section["value"]["display_filter_section"] is True
        assert [
            q["value"]["question"] for q in draft_section["value"]["questions"]
        ] == ["New Q"]

    def test_replace_avoids_anchors_of_other_sections_only(self, page, admin_user):
        data = to_csv(
            [
                ["question", "answer", "filtertag"],
                ["File", "A", "Filing"],
                ["Appeal", "A", "Filing"],
            ]
        )
        faq_section_import_csv(
            request=self.request(admin_user),
            page=page,
            data=data,
            section_id="top-section",
        )
        draft_section = faq_sections_list(self.latest(page))[0]
        assert [
            q["value"]["anchortag"] for q in draft_section["value"]["questions"]
        ] == [
            "file",
            "appeal-2",
        ]

    def test_replaces_nested_section(self, page, admin_user):
        data = to_csv(
            [["question", "answer", "filtertag"], ["Nested Q", "A", "Filing"]]
        )
        faq_section_import_csv(
            request=self.request(admin_user),
            page=page,
            data=data,
            section_id="nested-section",
        )
        top, nested = faq_sections_list(self.latest(page))
        assert top["value"]["questions"][0]["value"]["question"] == "How do I file"
        assert nested["value"]["questions"][0]["value"]["question"] == "Nested Q"

    def test_add_appends_a_new_section(self, page, admin_user):
        data = to_csv([["question", "answer", "filtertag"], ["Added", "A", "Filing"]])
        faq_section_import_csv(
            request=self.request(admin_user),
            page=page,
            data=data,
            display_filter_section=True,
        )
        latest = self.latest(page)
        assert latest.body[-1].block_type == "questionanswers"
        assert latest.body[-1].value["display_filter_section"] is True
        assert latest.body[-1].value["questions"][0]["question"] == "Added"

    @pytest.fixture
    def older_format_page(self, page):
        """``page`` with its nested section's questions stored as bare dicts."""
        revision = page.latest_revision
        body = json.loads(revision.content["body"])
        nested = body[1]["value"]["default_content"][0]["value"]
        nested["questions"] = [item["value"] for item in nested["questions"]]
        revision.content["body"] = json.dumps(body)
        revision.save()
        return page

    def test_replace_with_an_older_format_section_on_the_page(
        self, older_format_page, admin_user
    ):
        data = to_csv([["question", "answer", "filtertag"], ["Appeal", "A", "Filing"]])
        faq_section_import_csv(
            request=self.request(admin_user),
            page=older_format_page,
            data=data,
            section_id="top-section",
        )
        top = faq_sections_list(self.latest(older_format_page))[0]
        # "appeal" is taken by the older-format section
        assert top["value"]["questions"][0]["value"]["anchortag"] == "appeal-2"

    def test_add_with_an_older_format_section_on_the_page(
        self, older_format_page, admin_user
    ):
        data = to_csv([["question", "answer", "filtertag"], ["Added", "A", "Filing"]])
        faq_section_import_csv(
            request=self.request(admin_user),
            page=older_format_page,
            data=data,
        )
        latest = self.latest(older_format_page)
        assert latest.body[-1].value["questions"][0]["question"] == "Added"

    def test_invalid_csv_saves_nothing(self, page, admin_user):
        revisions = page.revisions.count()
        data = to_csv([["question", "answer", "filtertag"], ["Q", "A", "Nope"]])
        with pytest.raises(FAQCSVError):
            faq_section_import_csv(
                request=self.request(admin_user),
                page=page,
                data=data,
                section_id="top-section",
            )
        assert page.revisions.count() == revisions

    def test_unknown_section_saves_nothing(self, page, admin_user):
        revisions = page.revisions.count()
        data = to_csv([["question", "answer", "filtertag"], ["Q", "A", "Filing"]])
        with pytest.raises(FAQCSVError, match="no longer on the page"):
            faq_section_import_csv(
                request=self.request(admin_user),
                page=page,
                data=data,
                section_id="gone",
            )
        assert page.revisions.count() == revisions


class TestFaqCsvAdminViews:
    @pytest.fixture
    def client(self, admin_client, settings):
        settings.GITHUB_SHA = "test1234567"
        return admin_client

    def upload(self, client, page, rows, section_id=""):
        return client.post(
            reverse("faq_csv", args=[page.pk]),
            {
                "section_id": section_id,
                "csv_file": SimpleUploadedFile("faq.csv", to_csv(rows), "text/csv"),
            },
        )

    def test_index_lists_sections(self, client, page):
        content = client.get(reverse("faq_csv", args=[page.pk])).content.decode()
        assert reverse("faq_csv_download", args=[page.pk, "top-section"]) in content
        assert reverse("faq_csv_download", args=[page.pk, "nested-section"]) in content

    def test_download_returns_csv_with_byte_order_mark(self, client, page):
        response = client.get(
            reverse("faq_csv_download", args=[page.pk, "top-section"])
        )
        assert response["Content-Type"] == "text/csv; charset=utf-8"
        assert response["Content-Disposition"] == 'attachment; filename="faq-faq-1.csv"'
        assert response.content.startswith(
            b"\xef\xbb\xbfquestion,answer,filtertag,anchortag"
        )

    def test_download_unknown_section_is_404(self, client, page):
        assert (
            client.get(reverse("faq_csv_download", args=[page.pk, "gone"])).status_code
            == 404
        )

    def test_valid_upload_redirects_to_editor(self, client, page):
        response = self.upload(
            client,
            page,
            [["question", "answer", "filtertag"], ["Q", "A", "Filing"]],
            "top-section",
        )
        assert response.status_code == 302
        assert response.url == reverse("wagtailadmin_pages:edit", args=[page.pk])

    def test_invalid_upload_shows_errors_and_saves_nothing(self, client, page):
        revisions = page.revisions.count()
        response = self.upload(
            client,
            page,
            [["question", "answer", "filtertag"], ["Q", "A", "Nope"]],
            "top-section",
        )
        assert response.status_code == 400
        assert (
            "Row 2: FilterTag &quot;Nope&quot; does not exist"
            in response.content.decode()
        )
        assert page.revisions.count() == revisions

    def test_rejects_non_csv_file(self, client, page):
        response = client.post(
            reverse("faq_csv", args=[page.pk]),
            {"csv_file": SimpleUploadedFile("faq.xlsx", b"x")},
        )
        assert response.status_code == 400
        assert "Upload a .csv file." in response.content.decode()

    def test_other_page_types_are_404(self, client, page):
        home = page.get_parent()
        assert client.get(reverse("faq_csv", args=[home.pk])).status_code == 404

    def test_header_button_only_on_enhanced_standard_pages(self, page, admin_user):
        buttons = list(faq_csv_page_header_button(page, admin_user, "edit"))
        assert [b.url for b in buttons] == [reverse("faq_csv", args=[page.pk])]
        assert (
            list(faq_csv_page_header_button(page.get_parent(), admin_user, "edit"))
            == []
        )

    def test_page_editor_shows_header_button(self, client, page):
        response = client.get(reverse("wagtailadmin_pages:edit", args=[page.pk]))
        assert reverse("faq_csv", args=[page.pk]) in response.content.decode()

    @pytest.fixture
    def release_notes(self, page):
        release_notes = ReleaseNotes(title="Release notes", slug="release-notes")
        page.get_parent().add_child(instance=release_notes)
        release_notes.save_revision().publish()
        return release_notes

    @pytest.fixture
    def alias(self, page):
        return page.create_alias(update_slug="faq-alias")

    @pytest.mark.parametrize("target", ["release_notes", "alias"])
    def test_no_header_button(self, request, target, admin_user):
        target_page = request.getfixturevalue(target)
        assert list(faq_csv_page_header_button(target_page, admin_user, "edit")) == []

    @pytest.mark.parametrize("target", ["release_notes", "alias"])
    def test_index_is_404(self, request, client, target):
        target_page = request.getfixturevalue(target)
        assert client.get(reverse("faq_csv", args=[target_page.pk])).status_code == 404

    @pytest.mark.parametrize("target", ["release_notes", "alias"])
    def test_upload_is_404_and_saves_nothing(self, request, client, target):
        target_page = request.getfixturevalue(target)
        revisions = target_page.revisions.count()
        response = self.upload(
            client,
            target_page,
            [["question", "answer", "filtertag"], ["Q", "A", "Filing"]],
        )
        assert response.status_code == 404
        assert target_page.revisions.count() == revisions
