import pytest
from unittest.mock import patch
from django.test import RequestFactory
from app.urls import all_legacy_documents_redirect


# Class to instantiate fake documents (mocks weren't working well)
class FakeDoc:
    def __init__(self, filename, url, doc_id=1):
        self.id = doc_id
        self.filename = filename
        self.file = type("File", (), {"url": url, "name": filename})()


@pytest.mark.django_db
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


@pytest.mark.django_db
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


@pytest.mark.django_db
@patch("app.urls.render_404_util")
@patch("app.urls.Document")
def test_returns_404_on_multiple_matches(mock_document_model, mock_render_404):
    # Arrange
    doc1 = FakeDoc("test.pdf", "/media/documents/test.pdf")
    doc2 = FakeDoc("test.pdf", "/media/documents/folder/test.pdf")
    request = RequestFactory().get("/resources/test.pdf")
    mock_document_model.objects.filter.return_value = [doc1, doc2]

    # Act
    all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


@pytest.mark.django_db
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


@pytest.mark.django_db
@patch("app.urls.Document")
@patch("wagtail.documents.views.serve.serve")
def test_prevents_redirect_loop_for_files_documents_url(
    mock_wagtail_serve, mock_document_model
):
    # Arrange
    # Create a document with a file URL that would cause a redirect loop
    doc = FakeDoc("rule-1.pdf", "/files/documents/rule-1.pdf")
    mock_document_model.objects.filter.return_value = [doc]
    request = RequestFactory().get("/resources/rule-1.pdf")

    # Mock the Wagtail serve function to return a response
    from django.http import HttpResponse

    mock_wagtail_serve.return_value = HttpResponse(
        "PDF content", content_type="application/pdf"
    )

    # Act
    response = all_legacy_documents_redirect(request, "rule-1.pdf")

    # Assert
    # Should use Wagtail's serve function instead of redirecting
    mock_wagtail_serve.assert_called_once_with(request, doc.id, doc.filename)
    assert response.status_code == 200


@pytest.mark.django_db
@patch("app.urls.Document")
@patch("wagtail.documents.views.serve.serve")
def test_specific_rule_1_redirect_loop_prevention(
    mock_wagtail_serve, mock_document_model
):
    """Test the specific scenario from the debug logs: Rule-1_Amended_03202023.pdf -> rule-1.pdf"""
    # Arrange
    # Simulate the exact scenario from the logs
    doc = FakeDoc("rule-1.pdf", "/files/documents/rule-1.pdf")
    mock_document_model.objects.filter.return_value = [doc]

    # This simulates the request after the database redirect has already happened
    request = RequestFactory().get("/files/documents/rule-1.pdf")

    # Mock the Wagtail serve function to return a response
    from django.http import HttpResponse

    mock_wagtail_serve.return_value = HttpResponse(
        "PDF content", content_type="application/pdf"
    )

    # Act
    response = all_legacy_documents_redirect(request, "rule-1.pdf")

    # Assert
    # Should use Wagtail's serve function instead of redirecting (which would cause loop)
    mock_wagtail_serve.assert_called_once_with(request, doc.id, doc.filename)
    assert response.status_code == 200
    assert response.content == b"PDF content"


@pytest.mark.django_db
@patch("app.urls.Document")
def test_normal_redirect_still_works(mock_document_model):
    """Test that normal redirects (non-looping) still work as expected"""
    # Arrange
    # Document with normal media URL that won't cause loops
    doc = FakeDoc("test.pdf", "/media/documents/test.pdf")
    mock_document_model.objects.filter.return_value = [doc]
    request = RequestFactory().get("/resources/test.pdf")

    # Act
    response = all_legacy_documents_redirect(request, "test.pdf")

    # Assert
    # Should redirect normally since /media/documents/ won't cause loops
    assert response.status_code == 302
    assert response.url == "/media/documents/test.pdf"
