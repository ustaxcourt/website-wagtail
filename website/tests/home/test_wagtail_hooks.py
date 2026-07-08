"""Tests for home/wagtail_hooks.py signal handlers and hook functions."""

import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from django.test import RequestFactory, override_settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied


def _add_messages(request):
    setattr(request, "_messages", FallbackStorage(request))
    return request


def _make_get_request(path="/"):
    factory = RequestFactory()
    request = factory.get(path)
    request.session = {}
    _add_messages(request)
    return request


# ---------------------------------------------------------------------------
# prevent_navigation_menu_deletion
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPreventNavigationMenuDeletion:
    def test_raises_permission_denied_for_navigation_menu(self):
        from home.wagtail_hooks import prevent_navigation_menu_deletion
        from home.models import NavigationMenu

        request = _make_get_request()
        instance = NavigationMenu.__new__(NavigationMenu)
        with pytest.raises(PermissionDenied):
            prevent_navigation_menu_deletion(request, [instance])

    def test_allows_other_snippets(self):
        from home.wagtail_hooks import prevent_navigation_menu_deletion

        request = _make_get_request()
        non_nav_menu = object()
        prevent_navigation_menu_deletion(request, [non_nav_menu])


# ---------------------------------------------------------------------------
# protect_special_judge_roles
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestProtectSpecialJudgeRoles:
    def test_restricts_deletion_of_restricted_role_with_referer(self):
        from home.wagtail_hooks import protect_special_judge_roles
        from home.models.snippets.judges import JudgeRole, RESTRICTED_ROLES

        request = _make_get_request()
        request.META["HTTP_REFERER"] = "/admin/judges/"

        role = JudgeRole.__new__(JudgeRole)
        role.role_name = RESTRICTED_ROLES[0]

        response = protect_special_judge_roles(request, [role])
        assert response is not None
        assert response.status_code == 302
        assert "/admin/judges/" in response["Location"]

    def test_restricts_deletion_of_restricted_role_without_referer(self):
        from home.wagtail_hooks import protect_special_judge_roles
        from home.models.snippets.judges import JudgeRole, RESTRICTED_ROLES

        request = _make_get_request()
        request.META.pop("HTTP_REFERER", None)

        role = JudgeRole.__new__(JudgeRole)
        role.role_name = RESTRICTED_ROLES[0]

        response = protect_special_judge_roles(request, [role])
        assert response is not None
        assert response.status_code == 302

    def test_allows_deletion_of_non_restricted_role(self):
        from home.wagtail_hooks import protect_special_judge_roles
        from home.models.snippets.judges import JudgeRole

        request = _make_get_request()
        role = JudgeRole.__new__(JudgeRole)
        role.role_name = "Regular Judge"

        result = protect_special_judge_roles(request, [role])
        assert result is None

    def test_ignores_non_judge_role_snippets(self):
        from home.wagtail_hooks import protect_special_judge_roles

        request = _make_get_request()
        result = protect_special_judge_roles(request, [object()])
        assert result is None


# ---------------------------------------------------------------------------
# purge_cache_for_snippet_related_pages
# ---------------------------------------------------------------------------


class TestPurgeCacheForSnippetRelatedPages:
    def test_navigation_menu_triggers_root_purge(self):
        """NavigationMenu snippets map to '/' which matches every page, so a
        full-wildcard cache purge is used instead of enumerating every page."""
        from home.wagtail_hooks import purge_cache_for_snippet_related_pages

        request = MagicMock()

        class NavigationMenu:
            pass

        instance = NavigationMenu()

        with patch("home.wagtail_hooks.Page") as mock_page:
            mock_page.objects.live.return_value.filter.return_value = [
                MagicMock()
            ] * 250
            with patch("home.wagtail_hooks.purge_cloudflare_root") as mock_purge_root:
                with patch(
                    "home.wagtail_hooks.purge_pages_from_cache"
                ) as mock_purge_pages:
                    purge_cache_for_snippet_related_pages(request, instance)
        mock_purge_root.assert_called_once()
        mock_purge_pages.assert_not_called()

    def test_unknown_snippet_type_uses_root_prefix(self):
        """Unmapped snippet types fall back to '/', but with a small affected
        page count the cheaper scoped purge is still used."""
        from home.wagtail_hooks import purge_cache_for_snippet_related_pages

        request = MagicMock()
        instance = MagicMock()
        instance.__class__.__name__ = "UnknownSnippet"

        with patch("home.wagtail_hooks.Page") as mock_page:
            mock_page.objects.live.return_value.filter.return_value = [MagicMock()]
            with patch("home.wagtail_hooks.purge_pages_from_cache") as mock_purge:
                purge_cache_for_snippet_related_pages(request, instance)
                mock_purge.assert_called_once()

    def test_large_affected_page_set_uses_wildcard_purge(self):
        """Regardless of snippet type, once the affected page count exceeds the
        threshold, a single wildcard purge is used instead of purging pages
        individually (CloudFront bills per invalidation path)."""
        from home.wagtail_hooks import (
            purge_cache_for_snippet_related_pages,
            FULL_SITE_PURGE_PAGE_THRESHOLD,
        )

        request = MagicMock()
        instance = MagicMock()
        instance.__class__.__name__ = "Banner"

        with patch("home.wagtail_hooks.Page") as mock_page:
            mock_page.objects.live.return_value.filter.return_value = [MagicMock()] * (
                FULL_SITE_PURGE_PAGE_THRESHOLD + 1
            )
            with patch("home.wagtail_hooks.purge_cloudflare_root") as mock_purge_root:
                with patch(
                    "home.wagtail_hooks.purge_pages_from_cache"
                ) as mock_purge_pages:
                    purge_cache_for_snippet_related_pages(request, instance)
        mock_purge_root.assert_called_once()
        mock_purge_pages.assert_not_called()

    def test_private_seminar_disclosure_scoped_to_judges_prefix(self):
        """PrivateSeminarDisclosure only affects judge pages, so it should be
        scoped rather than falling back to a full-site purge."""
        from home.wagtail_hooks import purge_cache_for_snippet_related_pages

        request = MagicMock()
        instance = MagicMock()
        instance.__class__.__name__ = "PrivateSeminarDisclosure"

        with patch("home.wagtail_hooks.Page") as mock_page:
            mock_page.objects.live.return_value.filter.return_value = [MagicMock()]
            with patch("home.wagtail_hooks.purge_pages_from_cache") as mock_purge:
                purge_cache_for_snippet_related_pages(request, instance)
        mock_page.objects.live.return_value.filter.assert_called_once_with(
            url_path__startswith="/home/judges/"
        )
        mock_purge.assert_called_once()

    def test_no_affected_pages_does_not_purge(self):
        from home.wagtail_hooks import purge_cache_for_snippet_related_pages

        request = MagicMock()
        instance = MagicMock()
        instance.__class__.__name__ = "UnknownSnippet"

        with patch("home.wagtail_hooks.Page") as mock_page:
            mock_page.objects.live.return_value.filter.return_value = []
            with patch("home.wagtail_hooks.purge_pages_from_cache") as mock_purge:
                purge_cache_for_snippet_related_pages(request, instance)
                mock_purge.assert_not_called()

    def test_purge_cache_exception_is_handled(self):
        from home.wagtail_hooks import purge_cache_for_snippet_related_pages

        request = MagicMock()
        instance = MagicMock()
        instance.__class__.__name__ = "SimpleCard"

        with patch("home.wagtail_hooks.Page") as mock_page:
            mock_page.objects.live.return_value.filter.return_value = [MagicMock()]
            with patch(
                "home.wagtail_hooks.purge_pages_from_cache",
                side_effect=Exception("boom"),
            ):
                purge_cache_for_snippet_related_pages(request, instance)


# ---------------------------------------------------------------------------
# purge_cloudfront_cache_for_file
# ---------------------------------------------------------------------------


class TestPurgeCloudFrontCacheForFile:
    def test_http_url_extracts_path(self):
        from home.wagtail_hooks import purge_cloudfront_cache_for_file

        mock_batch = MagicMock()
        with patch("home.wagtail_hooks.PurgeBatch", return_value=mock_batch):
            with patch("home.wagtail_hooks.refresh_redirects_for_local_environments"):
                purge_cloudfront_cache_for_file(
                    "https://example.com/documents/test.pdf"
                )
        mock_batch.add_url.assert_called_once_with("/documents/test.pdf")

    def test_files_prefix_is_stripped(self):
        from home.wagtail_hooks import purge_cloudfront_cache_for_file

        mock_batch = MagicMock()
        with patch("home.wagtail_hooks.PurgeBatch", return_value=mock_batch):
            with patch("home.wagtail_hooks.refresh_redirects_for_local_environments"):
                purge_cloudfront_cache_for_file("/files/documents/test.pdf")
        mock_batch.add_url.assert_called_once_with("/documents/test.pdf")

    def test_relative_url_gets_slash_prepended(self):
        from home.wagtail_hooks import purge_cloudfront_cache_for_file

        mock_batch = MagicMock()
        with patch("home.wagtail_hooks.PurgeBatch", return_value=mock_batch):
            with patch("home.wagtail_hooks.refresh_redirects_for_local_environments"):
                purge_cloudfront_cache_for_file("documents/test.pdf")
        mock_batch.add_url.assert_called_once_with("/documents/test.pdf")

    def test_purge_exception_is_handled(self):
        from home.wagtail_hooks import purge_cloudfront_cache_for_file

        with patch("home.wagtail_hooks.PurgeBatch", side_effect=Exception("fail")):
            purge_cloudfront_cache_for_file("/documents/test.pdf")

    def test_refresh_redirects_exception_is_handled(self):
        from home.wagtail_hooks import purge_cloudfront_cache_for_file

        mock_batch = MagicMock()
        with patch("home.wagtail_hooks.PurgeBatch", return_value=mock_batch):
            with patch(
                "home.wagtail_hooks.refresh_redirects_for_local_environments",
                side_effect=Exception("refresh fail"),
            ):
                purge_cloudfront_cache_for_file("/documents/test.pdf")


# ---------------------------------------------------------------------------
# refresh_redirects_for_local_environments
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRefreshRedirectsForLocalEnvironments:
    @override_settings(ENVIRONMENT="local")
    def test_updates_redirect_in_local_env(self):
        from home.wagtail_hooks import refresh_redirects_for_local_environments
        from wagtail.contrib.redirects.models import Redirect
        from wagtail.models import Site

        site = Site.objects.first()
        redirect = Redirect(
            old_path="/old-path/test-file.pdf",
            redirect_link="/files/documents/test-file.pdf",
            site=site,
        )
        redirect.save()

        refresh_redirects_for_local_environments("/documents/test-file.pdf")

        redirect.refresh_from_db()
        assert redirect.redirect_link == "/documents/test-file.pdf"

    @override_settings(ENVIRONMENT="local")
    def test_no_matching_redirect_does_nothing(self):
        from home.wagtail_hooks import refresh_redirects_for_local_environments

        refresh_redirects_for_local_environments("/documents/nonexistent-file.pdf")

    @override_settings(ENVIRONMENT="production")
    def test_non_local_env_does_nothing(self):
        from home.wagtail_hooks import refresh_redirects_for_local_environments

        with patch("home.wagtail_hooks.Redirect") as mock_redirect:
            refresh_redirects_for_local_environments("/documents/test.pdf")
            mock_redirect.objects.filter.assert_not_called()

    @override_settings(ENVIRONMENT="local")
    def test_path_without_slash_does_not_crash(self):
        from home.wagtail_hooks import refresh_redirects_for_local_environments

        refresh_redirects_for_local_environments("nodirectory")


# ---------------------------------------------------------------------------
# Document signal handlers
# ---------------------------------------------------------------------------


class TestPurgeCacheAfterDocumentSave:
    def test_document_updated_triggers_purge(self):
        from home.wagtail_hooks import purge_cache_after_document_save

        instance = MagicMock()
        instance.url = "https://example.com/documents/test.pdf"

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_document_save(
                sender=None, instance=instance, created=False
            )
            mock_purge.assert_called_once_with(instance.url)

    def test_document_created_does_not_purge(self):
        from home.wagtail_hooks import purge_cache_after_document_save

        instance = MagicMock()
        instance.url = "https://example.com/documents/test.pdf"

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_document_save(
                sender=None, instance=instance, created=True
            )
            mock_purge.assert_not_called()

    def test_document_updated_with_no_url_logs_warning(self):
        """Updated document with no url attribute does not trigger a cache purge."""
        from home.wagtail_hooks import purge_cache_after_document_save

        instance = SimpleNamespace(title="Test Doc", id=1)

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_document_save(
                sender=None, instance=instance, created=False
            )
            mock_purge.assert_not_called()


class TestPurgeCacheAfterDocumentDelete:
    def test_document_with_url_triggers_purge(self):
        from home.wagtail_hooks import purge_cache_after_document_delete

        instance = MagicMock()
        instance.url = "https://example.com/documents/test.pdf"

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_document_delete(sender=None, instance=instance)
            mock_purge.assert_called_once_with(instance.url)

    def test_document_without_url_logs_warning(self):
        """Deleted document with no url attribute does not trigger a cache purge."""
        from home.wagtail_hooks import purge_cache_after_document_delete

        instance = SimpleNamespace(title="Test Doc", id=1)

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_document_delete(sender=None, instance=instance)
            mock_purge.assert_not_called()

    def test_document_with_empty_url_logs_warning(self):
        from home.wagtail_hooks import purge_cache_after_document_delete

        instance = MagicMock()
        instance.url = ""

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_document_delete(sender=None, instance=instance)
            mock_purge.assert_not_called()


# ---------------------------------------------------------------------------
# Image signal handlers
# ---------------------------------------------------------------------------


class TestPurgeCacheAfterImageSave:
    def test_image_with_file_url_triggers_purge(self):
        from home.wagtail_hooks import purge_cache_after_image_save

        instance = MagicMock()
        instance.file.url = "https://example.com/images/photo.jpg"

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_image_save(sender=None, instance=instance, created=False)
            mock_purge.assert_called_once_with("https://example.com/images/photo.jpg")

    def test_image_file_url_exception_is_handled(self):
        from home.wagtail_hooks import purge_cache_after_image_save

        instance = MagicMock()
        type(instance.file).url = property(
            lambda s: (_ for _ in ()).throw(Exception("no url"))
        )

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_image_save(sender=None, instance=instance, created=True)
            mock_purge.assert_not_called()

    def test_image_with_no_file_logs_warning(self):
        from home.wagtail_hooks import purge_cache_after_image_save

        instance = MagicMock()
        instance.file = None

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_image_save(sender=None, instance=instance, created=False)
            mock_purge.assert_not_called()


class TestPurgeCacheAfterImageDelete:
    def test_image_with_file_url_triggers_purge(self):
        from home.wagtail_hooks import purge_cache_after_image_delete

        instance = MagicMock()
        instance.file.url = "https://example.com/images/photo.jpg"

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_image_delete(sender=None, instance=instance)
            mock_purge.assert_called_once_with("https://example.com/images/photo.jpg")

    def test_image_without_file_logs_warning(self):
        from home.wagtail_hooks import purge_cache_after_image_delete

        instance = MagicMock()
        instance.file = None

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_image_delete(sender=None, instance=instance)
            mock_purge.assert_not_called()

    def test_image_file_url_exception_is_handled(self):
        from home.wagtail_hooks import purge_cache_after_image_delete

        instance = MagicMock()
        type(instance.file).url = property(
            lambda s: (_ for _ in ()).throw(Exception("no url"))
        )

        with patch("home.wagtail_hooks.purge_cloudfront_cache_for_file") as mock_purge:
            purge_cache_after_image_delete(sender=None, instance=instance)
            mock_purge.assert_not_called()


# ---------------------------------------------------------------------------
# NewsItem signal handlers
# ---------------------------------------------------------------------------


class TestPurgeNewsItemAffectedPages:
    def test_purges_affected_pages_when_found(self):
        from home.wagtail_hooks import _purge_newsitem_affected_pages

        with patch("home.wagtail_hooks.Page") as mock_page:
            mock_page.objects.live.return_value.filter.return_value = [MagicMock()]
            with patch("home.wagtail_hooks.purge_pages_from_cache") as mock_purge:
                _purge_newsitem_affected_pages()
                mock_purge.assert_called_once()

    def test_no_affected_pages_does_not_purge(self):
        from home.wagtail_hooks import _purge_newsitem_affected_pages

        with patch("home.wagtail_hooks.Page") as mock_page:
            mock_page.objects.live.return_value.filter.return_value = []
            with patch("home.wagtail_hooks.purge_pages_from_cache") as mock_purge:
                _purge_newsitem_affected_pages()
                mock_purge.assert_not_called()

    def test_purge_exception_is_handled(self):
        from home.wagtail_hooks import _purge_newsitem_affected_pages

        with patch("home.wagtail_hooks.Page") as mock_page:
            mock_page.objects.live.return_value.filter.return_value = [MagicMock()]
            with patch(
                "home.wagtail_hooks.purge_pages_from_cache",
                side_effect=Exception("fail"),
            ):
                _purge_newsitem_affected_pages()


class TestPurgeCacheAfterNewsItemSave:
    @pytest.mark.parametrize("created", [True, False], ids=["created", "updated"])
    def test_purge_called_on_save_or_update(self, created):
        """Purge is triggered whether the NewsItem is newly created or updated."""
        from home.wagtail_hooks import purge_cache_after_newsitem_save

        instance = MagicMock()
        instance.title = "Test"
        instance.id = 1

        with patch("home.wagtail_hooks._purge_newsitem_affected_pages") as mock_purge:
            purge_cache_after_newsitem_save(
                sender=None, instance=instance, created=created
            )
            mock_purge.assert_called_once()


class TestPurgeCacheAfterNewsItemDelete:
    def test_purge_called_on_delete(self):
        from home.wagtail_hooks import purge_cache_after_newsitem_delete

        instance = MagicMock()
        instance.title = "Test"
        instance.id = 1

        with patch("home.wagtail_hooks._purge_newsitem_affected_pages") as mock_purge:
            purge_cache_after_newsitem_delete(sender=None, instance=instance)
            mock_purge.assert_called_once()


# ---------------------------------------------------------------------------
# Header signal handler
# ---------------------------------------------------------------------------


class TestPurgeCacheAfterHeaderSave:
    def test_purge_called_on_header_save(self):
        from home.wagtail_hooks import purge_cache_after_header_save

        instance = MagicMock()
        instance.id = 1

        with patch("home.wagtail_hooks.purge_cloudflare_root") as mock_purge:
            purge_cache_after_header_save(sender=None, instance=instance, created=False)
            mock_purge.assert_called_once()


# ---------------------------------------------------------------------------
# notify_submitter_on_superseding_edit_of_draft_currently_in_moderation
# ---------------------------------------------------------------------------


class TestNotifySubmitterOnSupersedingEdit:
    def _hook_fn(self):
        from home.wagtail_hooks import (
            notify_submitter_on_superseding_edit_of_draft_currently_in_moderation,
        )

        return notify_submitter_on_superseding_edit_of_draft_currently_in_moderation

    def _make_request(self, user):
        factory = RequestFactory()
        request = factory.post("/admin/pages/1/edit/")
        request.user = user
        request.build_absolute_uri = lambda path="": f"https://example.com{path}"
        return request

    def test_returns_early_when_no_workflow_in_progress(self):
        """No email is sent when the page has no active workflow."""
        hook = self._hook_fn()
        page = MagicMock()
        page.workflow_in_progress = False
        request = self._make_request(MagicMock())
        with patch("home.wagtail_hooks.send_mail") as mock_send:
            hook(request, page)
            mock_send.assert_not_called()

    def test_returns_early_when_no_in_moderation_revision(self):
        """No email is sent when no revision is currently in moderation."""
        hook = self._hook_fn()
        page = MagicMock()
        page.workflow_in_progress = True
        page.current_workflow_state.revisions.return_value.latest.return_value = None
        request = self._make_request(MagicMock())
        with patch("home.wagtail_hooks.send_mail") as mock_send:
            hook(request, page)
            mock_send.assert_not_called()

    def test_returns_early_when_revision_has_no_user(self):
        """No email is sent when the in-moderation revision has no associated user."""
        hook = self._hook_fn()
        page = MagicMock()
        page.workflow_in_progress = True
        revision = MagicMock()
        revision.user = None
        page.current_workflow_state.revisions.return_value.latest.return_value = (
            revision
        )
        request = self._make_request(MagicMock())
        with patch("home.wagtail_hooks.send_mail") as mock_send:
            hook(request, page)
            mock_send.assert_not_called()

    def test_returns_early_when_submitter_is_same_as_editor(self):
        """No email is sent when the editor is the same person who submitted for review."""
        hook = self._hook_fn()
        user = MagicMock()
        page = MagicMock()
        page.workflow_in_progress = True
        revision = MagicMock()
        revision.user = user
        page.current_workflow_state.revisions.return_value.latest.return_value = (
            revision
        )
        request = self._make_request(user)
        with patch("home.wagtail_hooks.send_mail") as mock_send:
            hook(request, page)
            mock_send.assert_not_called()

    def test_sends_email_when_different_editor(self):
        hook = self._hook_fn()
        submitter = MagicMock()
        submitter.email = "submitter@example.com"
        editor = MagicMock()

        page = MagicMock()
        page.id = 1
        page.workflow_in_progress = True
        page.get_admin_display_title.return_value = "Test Page"
        revision = MagicMock()
        revision.user = submitter
        page.current_workflow_state.revisions.return_value.latest.return_value = (
            revision
        )

        request = self._make_request(editor)
        request.build_absolute_uri = MagicMock(
            return_value="https://example.com/admin/pages/1/edit/"
        )

        with patch("home.wagtail_hooks.render_to_string", return_value="<p>email</p>"):
            with patch("home.wagtail_hooks.send_mail") as mock_send:
                with patch(
                    "home.wagtail_hooks.reverse", return_value="/admin/pages/1/edit/"
                ):
                    hook(request, page)
                mock_send.assert_called_once()
                call_kwargs = mock_send.call_args
                assert submitter.email in call_kwargs[1]["recipient_list"]
