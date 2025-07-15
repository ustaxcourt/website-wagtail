import pytest
from unittest.mock import patch
from django.test import RequestFactory
from app.urls import all_legacy_documents_redirect


# Class to instantiate fake documents (mocks weren't working well)
class FakeDoc:
    def __init__(self, filename, url):
        self.filename = filename
        self.file = type("File", (), {"url": url})()


@pytest.mark.django_db
@patch("app.urls.Document")
@patch("app.urls.Redirect")
def test_redirects_on_exact_match(mock_redirect_model, mock_document_model):
    # Arrange
    doc = FakeDoc("test.pdf", "/media/documents/test.pdf")
    mock_redirect_model.objects.filter.return_value.first.return_value = None
    mock_document_model.objects.filter.return_value = [doc]
    request = RequestFactory().get("/resources/test.pdf")

    # Act
    response = all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    assert response.status_code == 302
    assert response.url == doc.file.url


@pytest.mark.django_db
@patch("app.urls.render_404_util")
@patch("app.urls.Document")
@patch("app.urls.Redirect")
def test_returns_404_on_no_matches(
    mock_redirect_model, mock_document_model, mock_render_404
):
    # Arrange
    mock_redirect_model.objects.filter.return_value.first.return_value = None
    mock_document_model.objects.filter.return_value = []
    request = RequestFactory().get("/resources/test.pdf")
    # Act
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


@pytest.mark.django_db
@patch("app.urls.render_404_util")
@patch("app.urls.Document")
@patch("app.urls.Redirect")
def test_returns_404_on_multiple_matches(
    mock_redirect_model, mock_document_model, mock_render_404
):
    # Arrange
    mock_redirect_model.objects.filter.return_value.first.return_value = None
    doc1 = FakeDoc("test.pdf", "/media/documents/test.pdf")
    doc2 = FakeDoc("test_2024.pdf", "/media/documents/test_2024.pdf")
    mock_document_model.objects.filter.return_value = [doc1, doc2]
    request = RequestFactory().get("/resources/test.pdf")

    # Act
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


@pytest.mark.django_db
@patch("app.urls.render_404_util")
@patch("app.urls.Document")
@patch("app.urls.Redirect")
def test_returns_404_on_single_non_exact_match(
    mock_redirect_model, mock_document_model, mock_render_404
):
    # Arrange
    mock_redirect_model.objects.filter.return_value.first.return_value = None
    doc = FakeDoc("test_2024.pdf", "/media/documents/test_2024.pdf")
    mock_document_model.objects.filter.return_value = [doc]
    request = RequestFactory().get("/resources/test.pdf")

    # Act
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)
