"""Tests for home/models/snippets/banners.py"""

import json
import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock, PropertyMock
from django.utils import timezone
from django.forms import ValidationError

from home.models.snippets.banners import Banner


class TestBannerCategory:
    def _make_banner(self, priority_level):
        obj = Banner.__new__(Banner)
        obj.priority_level = priority_level
        return obj

    def test_high_priority_category(self):
        banner = self._make_banner("high")
        assert banner.category == "High Priority"

    def test_critical_priority_category(self):
        banner = self._make_banner("critical")
        assert banner.category == "Critical"

    def test_other_priority_category(self):
        banner = self._make_banner("none")
        assert banner.category == "None"

    def test_str_returns_banner_title(self):
        obj = Banner.__new__(Banner)
        obj.banner_title = "Test Banner"
        assert str(obj) == "Test Banner"


class TestBannerCheckOverlapLogic:
    """Test _check_banner_overlap logic using mock querysets."""

    def _make_banner(self, priority="high", start_date=None, end_date=None, pk=1):
        obj = Banner.__new__(Banner)
        obj.id = pk
        obj.priority_level = priority
        obj.banner_start_date = start_date or timezone.now()
        obj.banner_end_date = end_date
        obj.banner_title = "Test Banner"
        return obj

    def test_no_overlap_when_no_other_banners(self):
        banner = self._make_banner()
        with patch.object(Banner, "objects") as mock_mgr:
            mock_mgr.filter.return_value.exclude.return_value.filter.return_value = []
            # Should not raise
            banner._check_banner_overlap("high")

    def test_overlap_when_other_banner_indefinite_and_this_also_indefinite(self):
        now = timezone.now()
        banner = self._make_banner(start_date=now, end_date=None, pk=2)

        other = MagicMock()
        other.banner_start_date = now - timedelta(hours=1)
        other.banner_end_date = None
        other.banner_title = "Existing Banner"

        with patch.object(Banner, "objects") as mock_mgr:
            mock_mgr.filter.return_value.exclude.return_value.filter.return_value = [
                other
            ]
            with pytest.raises(ValidationError):
                banner._check_banner_overlap("high")

    def test_no_overlap_when_other_banner_ends_before_this_starts(self):
        now = timezone.now()
        banner = self._make_banner(
            start_date=now + timedelta(hours=5),
            end_date=now + timedelta(hours=10),
            pk=2,
        )

        other = MagicMock()
        other.banner_start_date = now
        other.banner_end_date = now + timedelta(hours=3)  # ends before this one starts

        with patch.object(Banner, "objects") as mock_mgr:
            mock_mgr.filter.return_value.exclude.return_value.filter.return_value = [
                other
            ]
            # Should not raise
            banner._check_banner_overlap("high")


class TestBannerCleanValidation:
    def _make_banner(
        self, title="Test", description="Desc", priority="high", start_date=None
    ):
        obj = Banner.__new__(Banner)
        obj.id = 1
        obj.banner_title = title
        obj.description = description
        obj.priority_level = priority
        obj.banner_start_date = start_date
        obj.banner_end_date = None
        return obj

    def test_clean_missing_start_date_for_high_priority(self):
        banner = self._make_banner(priority="high", start_date=None)
        with patch.object(Banner, "clean", wraps=Banner.clean):
            with patch("home.models.snippets.banners.Banner._check_banner_overlap"):
                # Bypass the super().clean() call
                with patch("django.db.models.Model.clean"):
                    with pytest.raises(ValidationError) as exc_info:
                        Banner.clean(banner)
                    assert "banner_start_date" in exc_info.value.message_dict

    def test_clean_missing_start_date_for_critical_priority(self):
        banner = self._make_banner(priority="critical", start_date=None)
        with patch("django.db.models.Model.clean"):
            with pytest.raises(ValidationError) as exc_info:
                Banner.clean(banner)
            assert "banner_start_date" in exc_info.value.message_dict

    def test_clean_calls_overlap_check_when_start_date_set(self):
        banner = self._make_banner(priority="high", start_date=timezone.now())
        with patch("django.db.models.Model.clean"):
            with patch.object(banner, "_check_banner_overlap") as mock_check:
                with patch.object(Banner, "objects") as mock_mgr:
                    mock_mgr.filter.return_value.exclude.return_value.filter.return_value = []
                    Banner.clean(banner)
                    mock_check.assert_called_once_with("high")

    def test_category_property_accessed_from_banner(self):
        banner = self._make_banner(priority="high")
        assert banner.category == "High Priority"

    @pytest.mark.parametrize("priority", ["high", "critical"])
    def test_clean_allows_missing_start_date_in_preview(self, priority):
        """A banner can be previewed before a start date is set."""
        banner = self._make_banner(priority=priority, start_date=None)
        banner._is_preview = True
        with patch("django.db.models.Model.clean"):
            Banner.clean(banner)

    def test_clean_skips_overlap_check_in_preview(self):
        banner = self._make_banner(priority="high", start_date=timezone.now())
        banner._is_preview = True
        with patch("django.db.models.Model.clean"):
            with patch.object(banner, "_check_banner_overlap") as mock_check:
                Banner.clean(banner)
        mock_check.assert_not_called()

    def test_clean_still_requires_title_in_preview(self):
        banner = self._make_banner(title="", start_date=None)
        banner._is_preview = True
        with patch("django.db.models.Model.clean"):
            with pytest.raises(ValidationError) as exc_info:
                Banner.clean(banner)
        assert "banner_title" in exc_info.value.message_dict


@pytest.mark.django_db
class TestBannerOverlapDatabase:
    """Exercise _check_banner_overlap / clean() against real rows."""

    def _create(
        self, title="Existing", priority="high", start=None, end=None, live=True
    ):
        return Banner.objects.create(
            banner_title=title,
            description="Desc",
            priority_level=priority,
            banner_start_date=start,
            banner_end_date=end,
            live=live,
        )

    def _candidate(self, priority="high", start=None, end=None, title="New"):
        return Banner(
            banner_title=title,
            description="Desc",
            priority_level=priority,
            banner_start_date=start,
            banner_end_date=end,
        )

    def test_other_indefinite_and_self_indefinite_overlaps(self):
        now = timezone.now()
        self._create(start=now)
        with pytest.raises(ValidationError) as exc:
            self._candidate(start=now + timedelta(days=1))._check_banner_overlap("high")
        message = str(exc.value.message_dict["banner_start_date"])
        assert "indefinite" in message
        assert "Existing" in message

    def test_other_indefinite_starts_before_self_ends_overlaps(self):
        now = timezone.now()
        self._create(start=now)
        candidate = self._candidate(start=now, end=now + timedelta(days=2))
        with pytest.raises(ValidationError):
            candidate._check_banner_overlap("high")

    def test_other_indefinite_starts_after_self_ends_no_overlap(self):
        now = timezone.now()
        self._create(start=now + timedelta(days=10))
        candidate = self._candidate(start=now, end=now + timedelta(days=2))
        candidate._check_banner_overlap("high")

    def test_self_indefinite_other_ends_after_self_starts_overlaps(self):
        now = timezone.now()
        self._create(start=now, end=now + timedelta(days=5))
        candidate = self._candidate(start=now + timedelta(days=1))
        with pytest.raises(ValidationError) as exc:
            candidate._check_banner_overlap("high")
        # Finite end date is rendered, not "indefinite"
        assert "indefinite" not in str(exc.value.message_dict["banner_start_date"])

    def test_self_indefinite_other_ended_before_self_starts_no_overlap(self):
        now = timezone.now()
        self._create(start=now - timedelta(days=10), end=now - timedelta(days=5))
        self._candidate(start=now)._check_banner_overlap("high")

    def test_both_bounded_overlapping_raises(self):
        now = timezone.now()
        self._create(start=now, end=now + timedelta(days=5))
        candidate = self._candidate(
            start=now + timedelta(days=2), end=now + timedelta(days=8)
        )
        with pytest.raises(ValidationError):
            candidate._check_banner_overlap("high")

    def test_both_bounded_disjoint_no_overlap(self):
        now = timezone.now()
        self._create(start=now, end=now + timedelta(days=5))
        candidate = self._candidate(
            start=now + timedelta(days=6), end=now + timedelta(days=8)
        )
        candidate._check_banner_overlap("high")

    def test_different_priority_ignored(self):
        now = timezone.now()
        self._create(priority="critical", start=now)
        self._candidate(priority="high", start=now)._check_banner_overlap("high")

    def test_non_live_banner_ignored(self):
        now = timezone.now()
        self._create(start=now, live=False)
        self._candidate(start=now)._check_banner_overlap("high")

    def test_banner_does_not_overlap_itself(self):
        now = timezone.now()
        existing = self._create(start=now)
        existing._check_banner_overlap("high")

    def test_clean_raises_on_overlap(self):
        now = timezone.now()
        self._create(start=now)
        with pytest.raises(ValidationError) as exc:
            self._candidate(start=now).clean()
        assert "banner_start_date" in exc.value.message_dict

    def test_clean_passes_for_valid_banner(self):
        self._candidate(start=timezone.now()).clean()

    def test_clean_requires_title(self):
        banner = self._candidate(start=timezone.now(), title="")
        with pytest.raises(ValidationError) as exc:
            banner.clean()
        assert "banner_title" in exc.value.message_dict

    def test_clean_requires_description(self):
        banner = self._candidate(start=timezone.now())
        banner.description = ""
        with pytest.raises(ValidationError) as exc:
            banner.clean()
        assert "description" in exc.value.message_dict


@pytest.mark.django_db
class TestBannerQuerySetAndProperties:
    def _create(self, **kwargs):
        defaults = dict(banner_title="B", description="D", priority_level="high")
        defaults.update(kwargs)
        return Banner.objects.create(**defaults)

    def test_live_includes_started_unexpired_banner(self):
        banner = self._create(
            live=True, banner_start_date=timezone.now() - timedelta(hours=1)
        )
        assert banner in Banner.objects.live()

    def test_live_excludes_not_yet_started(self):
        banner = self._create(
            live=True, banner_start_date=timezone.now() + timedelta(days=1)
        )
        assert banner not in Banner.objects.live()

    def test_live_excludes_expired(self):
        banner = self._create(
            live=True,
            banner_start_date=timezone.now() - timedelta(days=2),
            expire_at=timezone.now() - timedelta(days=1),
        )
        assert banner not in Banner.objects.live()

    def test_live_excludes_draft(self):
        banner = self._create(
            live=False, banner_start_date=timezone.now() - timedelta(hours=1)
        )
        assert banner not in Banner.objects.live()

    def test_live_includes_future_expiry(self):
        banner = self._create(
            live=True,
            banner_start_date=timezone.now() - timedelta(days=1),
            expire_at=timezone.now() + timedelta(days=1),
        )
        assert banner in Banner.objects.live()

    def test_simple_properties(self):
        start = timezone.now()
        end = start + timedelta(days=1)
        banner = self._create(banner_start_date=start, banner_end_date=end)
        assert banner.title == "B"
        assert banner.publish_date == start
        assert banner.homepage_display_expiration_date == end
        assert list(banner.revisions.all()) == list(banner._revisions.all()) == []

    def test_document_url_dash_without_document(self):
        assert self._create().document_url == "-"

    def test_document_url_with_document(self):
        banner = Banner(banner_title="B")
        with patch.object(
            Banner, "document", new_callable=PropertyMock
        ) as mock_document:
            mock_document.return_value = MagicMock(url="/documents/1/banner.pdf")
            assert banner.document_url == "/documents/1/banner.pdf"

    def test_document_url_dash_when_document_has_no_url(self):
        banner = Banner(banner_title="B")
        banner.document = None
        assert banner.document_url == "-"


@pytest.mark.django_db
class TestBannerPreviewViews:
    """The admin preview endpoints accept a banner with no start date."""

    def _form_data(self, **overrides):
        data = {
            "banner_title": "No start date",
            "description": "Preview me",
            "priority_level": "high",
            "banner_start_date": "",
            "banner_end_date": "",
        }
        data.update(overrides)
        return data

    @pytest.fixture
    def admin_client(self, client, django_user_model, settings):
        settings.GITHUB_SHA = "test1234567"
        user = django_user_model.objects.create_superuser(
            username="preview-admin", email="preview@example.com", password="x"
        )
        client.force_login(user)
        return client

    def test_preview_on_create_is_valid_without_start_date(self, admin_client):
        response = admin_client.post(
            "/admin/snippets/home/banner/preview/", self._form_data()
        )
        assert response.json() == {"is_valid": True, "is_available": True}

    def test_preview_on_edit_is_valid_without_start_date(self, admin_client):
        banner = Banner.objects.create(
            banner_title="Existing",
            description="Desc",
            priority_level="critical",
            live=False,
        )
        response = admin_client.post(
            f"/admin/snippets/home/banner/preview/{banner.pk}/",
            self._form_data(priority_level="critical"),
        )
        assert response.json() == {"is_valid": True, "is_available": True}

    def test_preview_shows_message_when_no_announcements_page(self, admin_client):
        """With no News & Announcements page, the preview explains why instead of erroring."""
        url = "/admin/snippets/home/banner/preview/"
        admin_client.post(url, self._form_data())
        response = admin_client.get(url, {"mode": "announcements_page"})
        assert response.status_code == 200
        assert "Unable to render a preview" in response.content.decode()

    def test_saving_still_requires_start_date(self, admin_client):
        response = admin_client.post(
            "/admin/snippets/home/banner/add/", self._form_data()
        )
        assert not Banner.objects.filter(banner_title="No start date").exists()
        assert "Start date and time are required" in response.content.decode()


class TestBannerPreview:
    """Test the single-preview support (preview_modes, get_preview_template,
    get_preview_context, as_press_release_entry)."""

    def _make_banner(self, priority="high", start_date=None):
        banner = Banner()
        banner.banner_title = "Important Banner"
        banner.description = "Details"
        banner.priority_level = priority
        banner.banner_start_date = start_date or timezone.now()
        banner.document = None
        return banner

    def test_preview_modes_exposes_a_single_announcements_page_mode(self):
        """
        Only one preview mode is exposed (rather than a dropdown switcher),
        since the announcements-page preview already shows both the
        top-of-page banner and the historical listing entry together.
        """
        banner = self._make_banner()
        assert banner.preview_modes == [
            ("announcements_page", "News & Announcements page")
        ]

    def test_get_preview_template_uses_real_page_template(self):
        banner = self._make_banner()
        fake_page = MagicMock()
        fake_page.get_template.return_value = "home/press_release_page.html"
        with patch.object(
            Banner, "_get_preview_announcements_page", return_value=fake_page
        ):
            template = banner.get_preview_template(None, "announcements_page")
        assert template == "home/press_release_page.html"
        fake_page.get_template.assert_called_once_with(None)

    def test_get_preview_template_falls_back_when_no_page(self):
        banner = self._make_banner()
        with patch.object(Banner, "_get_preview_announcements_page", return_value=None):
            template = banner.get_preview_template(None, "announcements_page")
        assert template == "previews/banner_announcements_page_unavailable.html"

    def test_get_preview_context_includes_banner(self):
        banner = self._make_banner()
        with patch.object(Banner, "_get_preview_announcements_page", return_value=None):
            context = banner.get_preview_context(None, "announcements_page")
        assert context["banner"] is banner

    def test_get_preview_context_merges_page_context(self):
        banner = self._make_banner(priority="critical")
        fake_page = MagicMock()
        fake_page.get_context.return_value = {
            "press_releases_by_year": {2024: ["fake entry"]}
        }
        with patch.object(
            Banner, "_get_preview_announcements_page", return_value=fake_page
        ):
            context = banner.get_preview_context(None, "announcements_page")

        assert context["banner"] is banner
        assert context["press_releases_by_year"] == {2024: ["fake entry"]}
        fake_page.get_context.assert_called_once_with(None, preview_banner=banner)

    def test_get_preview_context_handles_missing_page(self):
        banner = self._make_banner()
        with patch.object(Banner, "_get_preview_announcements_page", return_value=None):
            context = banner.get_preview_context(None, "announcements_page")
        assert context["banner"] is banner
        assert "press_releases_by_year" not in context

    def test_as_press_release_entry_matches_priority_label(self):
        banner = self._make_banner(priority="high")
        entry = banner.as_press_release_entry()
        assert entry["banner_label"] == "High Priority"
        assert entry["banner_title"] == "Important Banner"
        assert entry["release_date"] == banner.banner_start_date.date()

    def test_as_press_release_entry_handles_missing_start_date(self):
        banner = self._make_banner()
        banner.banner_start_date = None
        entry = banner.as_press_release_entry()
        assert entry["release_date"] is None

    def test_as_press_release_entry_force_release_date_overrides_start_date(self):
        banner = self._make_banner()
        forced = timezone.now().replace(year=2010).date()
        entry = banner.as_press_release_entry(force_release_date=forced)
        assert entry["release_date"] == forced

    def test_as_press_release_entry_force_release_date_used_when_no_start_date(self):
        banner = self._make_banner()
        banner.banner_start_date = None
        forced = timezone.now().date()
        entry = banner.as_press_release_entry(force_release_date=forced)
        assert entry["release_date"] == forced

    def test_get_preview_context_announcements_page_forces_yellow_top_banner(self):
        """
        The announcements-page preview should also force the top-of-page
        yellow banner to display this banner, ignoring live status/dates,
        since base.html's yellow_news_banner.html otherwise only shows
        genuinely live banners within their scheduled window.
        """
        banner = self._make_banner(priority="high")
        fake_page = MagicMock()
        fake_page.get_context.return_value = {}
        with patch.object(
            Banner, "_get_preview_announcements_page", return_value=fake_page
        ):
            context = banner.get_preview_context(None, "announcements_page")

        assert context["has_yellow_news"] is True
        payload = json.loads(context["yellow_priority_news_json"])
        assert payload[0]["title"] == "Important Banner"
        assert payload[0]["banner_start_date"] is None
        assert payload[0]["banner_end_date"] is None
        # The live critical (red) banner remains supplied by its context
        # processor because preview context does not override that slot.
        assert "has_critical_news" not in context
        assert "critical_priority_news_json" not in context

    @pytest.mark.parametrize(
        "start_offset,end_offset",
        [
            (timedelta(days=2), None),
            (-timedelta(days=2), -timedelta(days=1)),
        ],
        ids=["future-start", "past-end"],
    )
    def test_preview_top_banner_ignores_schedule_dates(self, start_offset, end_offset):
        now = timezone.now()
        banner = self._make_banner(start_date=now + start_offset)
        banner.banner_end_date = now + end_offset if end_offset is not None else None
        banner.live = False
        fake_page = MagicMock()
        fake_page.get_context.return_value = {}

        with patch.object(
            Banner, "_get_preview_announcements_page", return_value=fake_page
        ):
            context = banner.get_preview_context(None, "announcements_page")

        payload = json.loads(context["yellow_priority_news_json"])
        assert payload[0]["title"] == "Important Banner"
        assert payload[0]["banner_start_date"] is None
        assert payload[0]["banner_end_date"] is None

    def test_get_preview_context_announcements_page_forces_critical_top_banner(self):
        banner = self._make_banner(priority="critical")
        fake_page = MagicMock()
        fake_page.get_context.return_value = {}
        with patch.object(
            Banner, "_get_preview_announcements_page", return_value=fake_page
        ):
            context = banner.get_preview_context(None, "announcements_page")

        assert context["has_critical_news"] is True
        payload = json.loads(context["critical_priority_news_json"])
        assert payload[0]["title"] == "Important Banner"
        assert payload[0]["banner_start_date"] is None
        # The live high priority (yellow) banner remains supplied by its
        # context processor because preview context does not override that slot.
        assert "has_yellow_news" not in context
        assert "yellow_priority_news_json" not in context

    def test_get_preview_context_announcements_page_skips_top_banner_for_none_priority(
        self,
    ):
        """A no-priority banner is not forced into a top slot, and existing
        live priority banners remain supplied by their context processors."""
        banner = self._make_banner(priority="none")
        fake_page = MagicMock()
        fake_page.get_context.return_value = {}
        with patch.object(
            Banner, "_get_preview_announcements_page", return_value=fake_page
        ):
            context = banner.get_preview_context(None, "announcements_page")

        assert "has_yellow_news" not in context
        assert "has_critical_news" not in context

    @pytest.mark.parametrize("priority", ["high", "critical", "none"])
    def test_get_preview_context_sets_is_banner_preview(self, priority):
        """
        is_banner_preview tells yellow_news_banner.html to ignore localStorage
        dismissals, so dismissing in a preview never hides the live banner.
        """
        banner = self._make_banner(priority=priority)
        with patch.object(Banner, "_get_preview_announcements_page", return_value=None):
            context = banner.get_preview_context(None, "announcements_page")
        assert context["is_banner_preview"] is True


class TestYellowNewsBannerTemplatePreviewFlag:
    """yellow_news_banner.html only skips localStorage dismissals in a preview."""

    def _render(self, **extra):
        from django.template.loader import render_to_string

        context = {"has_yellow_news": True, "yellow_priority_news_json": "[]"}
        context.update(extra)
        return render_to_string("yellow_news_banner.html", context)

    def test_flag_is_false_on_normal_pages(self):
        assert "var IS_BANNER_PREVIEW = false;" in self._render()

    def test_flag_is_true_in_banner_preview(self):
        html = self._render(is_banner_preview=True)
        assert "var IS_BANNER_PREVIEW = true;" in html
