import os
from unittest.mock import patch
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django.http import Http404
from django.conf import settings
from app.urls import all_legacy_documents_redirect, render_legacy_404  # adjust import as needed
from wagtail.documents.models import Document


@patch("app.urls.Document")
def test_redirects_on_exact_match(mock_document_model):
    class FakeDoc:
        def __init__(self, filename, url):
            self.filename = filename
            self.file = type("File", (), {"url": url})()

    doc = FakeDoc("test.pdf", "/media/documents/test.pdf")
    mock_document_model.objects.filter.return_value = [doc]

    request = RequestFactory().get("/resources/test.pdf")
    response = all_legacy_documents_redirect(request, "test.pdf")

    assert response.status_code == 302
    assert response.url == doc.file.url

@patch("app.urls.render_legacy_404")
@patch("app.urls.Document")
def test_returns_404_on_non_pdf_file(mock_document_model, mock_render_404):
    class FakeDoc:
        def __init__(self, filename, url):
            self.filename = filename
            self.file = type("File", (), {"url": url})()

    doc = FakeDoc("test.pdf", "/media/documents/test.pdf")
    request = RequestFactory().get("/resources/test.pdf")
    mock_document_model.objects.filter.return_value = [doc]
    response = all_legacy_documents_redirect(request, "test.docx")
    mock_render_404.assert_called_once_with(request, "test.docx")


@patch("app.urls.render_legacy_404")
@patch("app.urls.Document")
def test_returns_404_on_no_matches(mock_document_model, mock_render_404):
    request = RequestFactory().get("/resources/test.pdf")

    mock_document_model.objects.filter.return_value = []

    all_legacy_documents_redirect(request, "test.pdf")

    mock_render_404.assert_called_once_with(request, "test.pdf")

@patch("app.urls.render_legacy_404")
@patch("app.urls.Document")
def test_returns_404_on_multiple_matches(mock_document_model, mock_render_404):
    #rewrite
    class FakeDoc:
        def __init__(self, filename, url):
            self.filename = filename
            self.file = type("File", (), {"url": url})()

    doc1 = FakeDoc("test.pdf", "/media/documents/test.pdf")
    doc2 = FakeDoc("test_2024.pdf", "/media/documents/test_2024.pdf")
    
    request = RequestFactory().get("/resources/test.pdf")

    mock_document_model.objects.filter.return_value = [doc1, doc2]

    all_legacy_documents_redirect(request, "test.pdf")

    mock_render_404.assert_called_once_with(request, "test.pdf")
    
@patch("app.urls.render_legacy_404")
@patch("app.urls.Document")
def test_returns_404_on_single_non_exact_match(mock_document_model, mock_render_404):
    class FakeDoc:
        def __init__(self, filename, url):
            self.filename = filename
            self.file = type("File", (), {"url": url})()

    doc = FakeDoc("test_2024.pdf", "/media/documents/test_2024.pdf")
    
    request = RequestFactory().get("/resources/test.pdf")

    mock_document_model.objects.filter.return_value = [doc]

    all_legacy_documents_redirect(request, "test.pdf")

    mock_render_404.assert_called_once_with(request, "test.pdf")
    
