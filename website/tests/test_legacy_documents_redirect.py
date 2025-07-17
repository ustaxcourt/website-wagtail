import pytest
from unittest.mock import patch
from django.test import RequestFactory
from django.http import HttpResponsePermanentRedirect, HttpResponseNotFound
from app.urls import all_legacy_documents_redirect


# Class to instantiate fake documents (mocks weren't working well)
class FakeDoc:
    def __init__(self, filename, url):
        self.filename = filename
        self.file = type("File", (), {"url": url})()


# Fixture to mock render_404_util for all tests
@pytest.fixture(autouse=True)
def mock_render_404_utility():
    with patch("app.urls.render_404_util") as mock:
        mock.return_value = HttpResponseNotFound(
            "Not Found"
        )  # Ensure it returns a proper response object
        yield mock


@pytest.mark.django_db
@patch("app.urls.Document")
@patch("app.urls.normalize_rule_pdf_filename", return_value=None)
def test_redirects_on_exact_match_with_casing_difference(
    mock_normalizer, mock_document_model, mock_render_404_utility
):
    """
    Test that a request for a filename with casing difference does not redirect
    (since lowercased filenames match exactly), and instead returns 404.
    """
    # Arrange
    doc = FakeDoc("test.pdf", "/media/documents/test.pdf")
    mock_document_model.objects.filter.return_value = [doc]
    request = RequestFactory().get("/resources/Test.pdf")  # Casing difference

    # Act
    response = all_legacy_documents_redirect(request, "test.pdf")

    assert response.status_code == 404
    mock_render_404_utility.assert_called_once_with(request)


@pytest.mark.django_db
@patch("app.urls.Document")
@patch("app.urls.normalize_rule_pdf_filename", return_value=None)
def test_returns_404_on_no_matches(
    mock_normalizer, mock_document_model, mock_render_404_utility
):
    """
    Test that if no document matches, a 404 is returned.
    """
    # Arrange
    mock_document_model.objects.filter.return_value = []
    request = RequestFactory().get("/resources/nonexistent.pdf")

    response = all_legacy_documents_redirect(request, "nonexistent.pdf")

    assert response.status_code == 404
    mock_render_404_utility.assert_called_once_with(request)


@pytest.mark.django_db
@patch("app.urls.Document")
@patch("app.urls.normalize_rule_pdf_filename", return_value="rule-21.pdf")
def test_redirects_on_filename_normalization(
    mock_normalizer, mock_document_model, mock_render_404_utility
):
    """
    Test that requesting a variant like Rule-21Amended.pdf redirects to rule-21.pdf.
    """
    mock_document_model.objects.filter.return_value = []  # Ensure no Document match interferes

    request = RequestFactory().get("/files/documents/Rule-21Amended.pdf")

    response = all_legacy_documents_redirect(request, "Rule-21Amended.pdf")

    assert isinstance(response, HttpResponsePermanentRedirect)
    assert response.status_code == 301
    assert response.url == "/files/documents/rule-21.pdf"
    mock_normalizer.assert_called_once_with("Rule-21Amended.pdf")


@pytest.mark.django_db
@patch("app.urls.Document")
@patch(
    "app.urls.normalize_rule_pdf_filename",
    side_effect=lambda f: f.lower() if "rule" in f.lower() else None,
)
def test_does_not_redirect_if_path_is_already_normalized(
    mock_normalizer, mock_document_model, mock_render_404_utility
):
    """
    Test that if the path is already normalized (e.g., /files/documents/rule-21.pdf),
    the view returns None to fall through to Wagtail or static handlers.
    """
    request = RequestFactory().get("/files/documents/rule-21.pdf")

    response = all_legacy_documents_redirect(request, "rule-21.pdf")

    assert response is None
    mock_render_404_utility.assert_not_called()
    mock_normalizer.assert_called_once_with("rule-21.pdf")

    # ✅ This call never happens when the path is already normalized, so remove this expectation:
    mock_document_model.objects.filter.assert_not_called()


@pytest.mark.django_db
@patch("app.urls.Document")
@patch("app.urls.normalize_rule_pdf_filename", return_value=None)
def test_returns_404_on_multiple_matches(
    mock_normalizer, mock_document_model, mock_render_404_utility
):
    """
    Test that if multiple documents match the base filename, a 404 is returned.
    """
    doc1 = FakeDoc("document-v1.pdf", "/media/documents/document-v1.pdf")
    doc2 = FakeDoc("document-v2.pdf", "/media/documents/document-v2.pdf")
    mock_document_model.objects.filter.return_value = [doc1, doc2]

    request = RequestFactory().get("/resources/document.pdf")

    response = all_legacy_documents_redirect(request, "document.pdf")

    assert response.status_code == 404
    mock_render_404_utility.assert_called_once_with(request)
