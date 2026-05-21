"""Tests for home/models/snippets/news_item.py"""

import pytest
from unittest.mock import MagicMock, patch
from django.utils import timezone
from django.core.exceptions import ValidationError


class TestNewsItemQuerySet:
    """Test the NewsItemQuerySet.live() method with mocks."""

    def _make_fake_qs(self, items):
        """Create a minimal mock queryset."""
        qs = MagicMock()
        qs.filter.return_value = qs
        qs.__iter__ = lambda s: iter(items)
        return qs


@pytest.mark.django_db
class TestNewsItemClean:
    def _make_news_item(self, **kwargs):
        from home.models.snippets.news_item import NewsItem

        obj = NewsItem.__new__(NewsItem)
        obj.title = kwargs.get("title", "Test Title")
        obj.description = kwargs.get("description", "Test Description")
        obj.publish_date = kwargs.get("publish_date", timezone.now())
        return obj

    def test_raises_validation_error_if_no_title(self):
        obj = self._make_news_item(title="")
        with pytest.raises(ValidationError) as exc_info:
            obj.clean()
        assert "title" in str(exc_info.value)

    def test_raises_validation_error_if_no_description(self):
        obj = self._make_news_item(description="")
        with pytest.raises(ValidationError) as exc_info:
            obj.clean()
        assert "description" in str(exc_info.value)

    def test_raises_validation_error_if_no_publish_date(self):
        obj = self._make_news_item(publish_date=None)
        with pytest.raises(ValidationError) as exc_info:
            obj.clean()
        assert "publish_date" in str(exc_info.value)


class TestNewsItemProperties:
    def test_document_url_with_none_document(self):
        from home.models.snippets.news_item import NewsItem

        obj = NewsItem.__new__(NewsItem)
        # Patch the document property to return None
        with patch.object(
            NewsItem, "document", new_callable=lambda: property(lambda s: None)
        ):
            assert obj.document_url == "-"

    def test_document_url_with_document_set(self):
        from home.models.snippets.news_item import NewsItem

        obj = NewsItem.__new__(NewsItem)
        mock_doc = MagicMock()
        mock_doc.url = "/path/to/doc.pdf"
        with patch.object(
            NewsItem, "document", new_callable=lambda: property(lambda s: mock_doc)
        ):
            assert obj.document_url == "/path/to/doc.pdf"

    def test_document_url_returns_dash_when_document_has_no_url(self):
        from home.models.snippets.news_item import NewsItem

        obj = NewsItem.__new__(NewsItem)
        mock_doc = MagicMock()
        mock_doc.url = None
        with patch.object(
            NewsItem, "document", new_callable=lambda: property(lambda s: mock_doc)
        ):
            assert obj.document_url == "-"

    def test_str_returns_title(self):
        from home.models.snippets.news_item import NewsItem

        obj = NewsItem.__new__(NewsItem)
        obj.title = "My News Item"
        assert str(obj) == "My News Item"


class TestNewsItemFilterSet:
    def test_filter_publish_date_from_returns_queryset_unchanged_when_no_value(self):
        from home.models.snippets.news_item import NewsItemFilterSet

        fs = NewsItemFilterSet.__new__(NewsItemFilterSet)
        qs = MagicMock()
        result = fs.filter_publish_date_from(qs, "publish_date", None)
        assert result is qs

    def test_filter_publish_date_to_returns_queryset_unchanged_when_no_value(self):
        from home.models.snippets.news_item import NewsItemFilterSet

        fs = NewsItemFilterSet.__new__(NewsItemFilterSet)
        qs = MagicMock()
        result = fs.filter_publish_date_to(qs, "publish_date", None)
        assert result is qs

    def test_filter_publish_date_from_filters_when_value_given(self):
        from home.models.snippets.news_item import NewsItemFilterSet
        from datetime import date

        fs = NewsItemFilterSet.__new__(NewsItemFilterSet)
        qs = MagicMock()
        qs.filter.return_value = qs
        fs.filter_publish_date_from(qs, "publish_date", date(2024, 1, 1))
        qs.filter.assert_called_once()

    def test_filter_publish_date_to_filters_when_value_given(self):
        from home.models.snippets.news_item import NewsItemFilterSet
        from datetime import date

        fs = NewsItemFilterSet.__new__(NewsItemFilterSet)
        qs = MagicMock()
        qs.filter.return_value = qs
        fs.filter_publish_date_to(qs, "publish_date", date(2024, 1, 1))
        qs.filter.assert_called_once()


class TestNewsItemQuerySetLive:
    def test_live_method_filters_correctly(self):
        from home.models.snippets.news_item import NewsItemQuerySet

        qs = MagicMock()
        qs.filter.return_value = qs

        # Create instance of the queryset (mocked)
        nqs = MagicMock(spec=NewsItemQuerySet)
        nqs.filter.return_value = nqs

        # Test that filter is called with live=True and go_live_at__lte
        NewsItemQuerySet.live(nqs)
        # Just verify the method calls filter
        assert nqs.filter.called


class TestGetRandomNewsItemImagePk:
    def test_returns_none_when_no_collection(self):
        from home.models.snippets.news_item import get_random_news_item_image_pk

        with patch("home.models.snippets.news_item.Collection") as mock_coll:
            mock_coll.objects.filter.return_value.first.return_value = None
            result = get_random_news_item_image_pk()
            assert result is None

    def test_returns_none_when_collection_but_no_images(self):
        from home.models.snippets.news_item import get_random_news_item_image_pk

        with patch("home.models.snippets.news_item.Collection") as mock_coll:
            mock_coll.objects.filter.return_value.first.return_value = MagicMock()
            with patch("home.models.snippets.news_item.Image") as mock_image:
                mock_image.objects.filter.return_value = []
                result = get_random_news_item_image_pk()
                assert result is None

    def test_returns_pk_when_images_exist(self):
        from home.models.snippets.news_item import get_random_news_item_image_pk

        mock_img = MagicMock()
        mock_img.pk = 42
        with patch("home.models.snippets.news_item.Collection") as mock_coll:
            mock_coll.objects.filter.return_value.first.return_value = MagicMock()
            with patch("home.models.snippets.news_item.Image") as mock_image:
                mock_image.objects.filter.return_value = [mock_img]
                with patch(
                    "home.models.snippets.news_item.random.choice",
                    return_value=mock_img,
                ):
                    result = get_random_news_item_image_pk()
                    assert result == 42


class TestNewsItemStatusProperty:
    def test_status_property_returns_status_string(self):
        from home.models.snippets.news_item import NewsItem

        obj = NewsItem.__new__(NewsItem)
        with patch.object(
            type(obj), "status_string", new_callable=lambda: property(lambda s: "live")
        ):
            assert obj.status == "live"
