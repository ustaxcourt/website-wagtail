from unittest.mock import patch
from django.test import RequestFactory
from app.urls import all_legacy_documents_redirect


# Class to instantiate fake documents (mocks weren't working well)
class FakeDoc:
    def __init__(self, filename, url):
        self.filename = filename
        self.file = type("File", (), {"url": url})()


@patch("app.urls.Document")
def test_redirects_on_exact_match(mock_document_model):
    # Arrange
    doc = FakeDoc("test.pdf", "/media/documents/test.pdf")
    mock_document_model.objects.filter.return_value = [doc]
    request = RequestFactory().get("/resources/test.pdf")

    # Act
    response = all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    assert response.status_code == 302
    assert response.url == doc.file.url


@patch("app.urls.render_404_util")
@patch("app.urls.Document")
def test_returns_404_on_no_matches(mock_document_model, mock_render_404):
    # Arrange
    request = RequestFactory().get("/resources/test.pdf")
    mock_document_model.objects.filter.return_value = []

    # Act
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


@patch("app.urls.render_404_util")
@patch("app.urls.Document")
def test_returns_404_on_multiple_matches(mock_document_model, mock_render_404):
    # Arrange
    doc1 = FakeDoc("test.pdf", "/media/documents/test.pdf")
    doc2 = FakeDoc("test_2024.pdf", "/media/documents/test_2024.pdf")
    request = RequestFactory().get("/resources/test.pdf")
    mock_document_model.objects.filter.return_value = [doc1, doc2]

    # Act
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


@patch("app.urls.render_404_util")
@patch("app.urls.Document")
def test_returns_404_on_single_non_exact_match(mock_document_model, mock_render_404):
    # Arrange
    doc = FakeDoc("test_2024.pdf", "/media/documents/test_2024.pdf")
    request = RequestFactory().get("/resources/test.pdf")
    mock_document_model.objects.filter.return_value = [doc]

    # Act
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)
