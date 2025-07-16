import pytest
from unittest.mock import patch
from django.test import RequestFactory
from app.urls import all_legacy_documents_redirect


# Class to instantiate fake documents (mocks weren't working well)
class FakeDoc:
    def __init__(self, filename, url):
        self.filename = filename
        self.file = type("File", (), {"url": url})()


# All legacy redirect paths
LEGACY_URL_PATHS = [
    "/resources/test.pdf",
    "/files/documents/test.pdf",
    "/documents/test.pdf",
]


@pytest.mark.django_db
@pytest.mark.parametrize("url_path", LEGACY_URL_PATHS)
@patch("app.urls.Document")
@patch("app.urls.Redirect")
def test_redirects_on_exact_match(mock_redirect_model, mock_document_model, url_path):
    doc = FakeDoc("test.pdf", "/media/documents/test.pdf")

    # Redirect model returns no DB match
    mock_redirect_model.objects.filter.return_value.first.return_value = None
    mock_document_model.objects.filter.return_value = [doc]

    request = RequestFactory().get(url_path)
    # Act
    response = all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    assert response.status_code == 302
    assert response.url == doc.file.url


@pytest.mark.django_db
@pytest.mark.parametrize("url_path", LEGACY_URL_PATHS)
@patch("app.urls.render_404_util")
@patch("app.urls.Document")
@patch("app.urls.Redirect")
def test_returns_404_on_no_matches(mock_redirect, mock_doc, mock_render_404, url_path):
    # Arrange
    mock_redirect.objects.filter.return_value.first.return_value = None
    mock_doc.objects.filter.return_value = []
    request = RequestFactory().get(url_path)
    # Act
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


@pytest.mark.django_db
@pytest.mark.parametrize("url_path", LEGACY_URL_PATHS)
@patch("app.urls.render_404_util")
@patch("app.urls.Document")
@patch("app.urls.Redirect")
def test_returns_404_on_multiple_matches(
    mock_redirect, mock_doc, mock_render_404, url_path
):
    # Arrange
    doc1 = FakeDoc("test.pdf", "/media/documents/test.pdf")
    doc2 = FakeDoc("test_copy.pdf", "/media/documents/test_copy.pdf")
    mock_redirect.objects.filter.return_value.first.return_value = None
    mock_doc.objects.filter.return_value = [doc1, doc2]

    request = RequestFactory().get(url_path)
    # Act
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


@pytest.mark.django_db
@pytest.mark.parametrize("url_path", LEGACY_URL_PATHS)
@patch("app.urls.render_404_util")
@patch("app.urls.Document")
@patch("app.urls.Redirect")
def test_returns_404_on_single_non_exact_match(
    mock_redirect, mock_doc, mock_render_404, url_path
):
    # Arrange
    doc = FakeDoc("test_2024.pdf", "/media/documents/test_2024.pdf")
    mock_redirect.objects.filter.return_value.first.return_value = None
    mock_doc.objects.filter.return_value = [doc]

    # Act
    request = RequestFactory().get(url_path)
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


# ✅ Canonical filename redirect tests


@pytest.mark.django_db
@patch("app.urls.Document")
def test_canonical_filename_redirect_if_normalized_exists(mock_doc_model):
    # Simulate: Rule-12superseded.pdf → rule-12.pdf
    mock_doc_model.objects.filter.return_value.exists.return_value = True

    request = RequestFactory().get("/files/documents/Rule-12superseded.pdf")
    response = all_legacy_documents_redirect(request, "Rule-12superseded.pdf")

    assert response.status_code == 301 or response.status_code == 302
    assert response.url == "/files/documents/rule-12.pdf"


@pytest.mark.django_db
@patch("app.urls.Document")
@patch("app.urls.render_404_util")
def test_canonical_filename_redirect_not_found(mock_render_404, mock_doc_model):
    # Simulate: Rule-99junk.pdf → rule-99.pdf not found
    mock_doc_model.objects.filter.return_value.exists.return_value = False

    request = RequestFactory().get("/files/documents/Rule-99junk.pdf")
    all_legacy_documents_redirect(request, "Rule-99junk.pdf")

    mock_render_404.assert_called_once_with(request)
