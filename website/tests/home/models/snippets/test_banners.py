"""Tests for home/models/snippets/banners.py"""

import json
import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock
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
        payload = context["yellow_priority_news"]
        assert payload[0]["title"] == "Important Banner"
        assert payload[0]["banner_start_date"] is None
        assert payload[0]["banner_end_date"] is None
        # Any live critical (red) banner is hidden so only the previewed
        # banner shows at the top of the page.
        assert context["has_critical_news"] is False
        assert context["critical_priority_news"] == []

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

        payload = context["yellow_priority_news"]
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
        payload = context["critical_priority_news"]
        assert payload[0]["title"] == "Important Banner"
        assert payload[0]["banner_start_date"] is None
        # Any live high priority (yellow) banner is hidden.
        assert context["has_yellow_news"] is False
        assert context["yellow_priority_news"] == []

    def test_get_preview_context_announcements_page_skips_top_banner_for_none_priority(
        self,
    ):
        """A banner with no priority level was never shown at the top of the
        page in production, so the preview shouldn't force it there either,
        and other live banners are still hidden."""
        banner = self._make_banner(priority="none")
        fake_page = MagicMock()
        fake_page.get_context.return_value = {}
        with patch.object(
            Banner, "_get_preview_announcements_page", return_value=fake_page
        ):
            context = banner.get_preview_context(None, "announcements_page")

        assert context["has_yellow_news"] is False
        assert context["has_critical_news"] is False

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


class TestBannerTemplateSecurity:
    @pytest.mark.parametrize(
        "template,context_key,flag,script_id",
        [
            (
                "yellow_news_banner.html",
                "yellow_priority_news",
                "has_yellow_news",
                "yellow-news-data",
            ),
            (
                "red_news_banner.html",
                "critical_priority_news",
                "has_critical_news",
                "critical-news-data",
            ),
        ],
    )
    def test_banner_json_cannot_close_script(
        self, template, context_key, flag, script_id
    ):
        from bs4 import BeautifulSoup
        from django.template.loader import render_to_string

        payload = [
            {
                "id": 1,
                "title": '</script><script>alert("banner")</script>',
                "description": "<h1>this should not allow html tags</h1>",
            }
        ]
        html = render_to_string(template, {flag: True, context_key: payload})
        document = BeautifulSoup(html, "html.parser")

        assert len(document.find_all("script")) == 2
        assert json.loads(document.find("script", id=script_id).string) == payload


class TestYellowNewsBannerTemplatePreviewFlag:
    """yellow_news_banner.html only skips localStorage dismissals in a preview."""

    def _render(self, **extra):
        from django.template.loader import render_to_string

        context = {"has_yellow_news": True, "yellow_priority_news": []}
        context.update(extra)
        return render_to_string("yellow_news_banner.html", context)

    def test_flag_is_false_on_normal_pages(self):
        assert "var IS_BANNER_PREVIEW = false;" in self._render()

    def test_flag_is_true_in_banner_preview(self):
        html = self._render(is_banner_preview=True)
        assert "var IS_BANNER_PREVIEW = true;" in html
