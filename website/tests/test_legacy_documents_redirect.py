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


@pytest.mark.django_db
@patch("app.urls.render_404_util")
@patch("wagtail.contrib.redirects.models.Redirect.objects")
def test_prevents_database_redirect_loop_to_same_function(
    mock_redirect_objects, mock_render_404
):
    """Test that database redirects that would trigger the same function are prevented"""
    # Arrange
    from types import SimpleNamespace

    # Mock a redirect that would cause a loop
    redirect_entry = SimpleNamespace()
    redirect_entry.old_path = "/files/documents/Rule-1_Amended_03202023.pdf"
    redirect_entry.redirect_link = "https://example.com/files/documents/rule-1.pdf"
    redirect_entry.site = "localhost"
    redirect_entry.is_permanent = True

    mock_redirect_objects.filter.return_value.first.return_value = redirect_entry

    request = RequestFactory().get("/files/documents/Rule-1_Amended_03202023.pdf")

    # Act
    all_legacy_documents_redirect(request, "Rule-1_Amended_03202023.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


@pytest.mark.django_db
@patch("app.urls.render_404_util")
@patch("wagtail.contrib.redirects.models.Redirect.objects")
def test_prevents_database_redirect_loop_to_relative_path(
    mock_redirect_objects, mock_render_404
):
    """Test that database redirects to relative paths that would trigger the same function are prevented"""
    # Arrange
    from types import SimpleNamespace

    # Mock a redirect that would cause a loop with relative path
    redirect_entry = SimpleNamespace()
    redirect_entry.old_path = "/files/documents/Rule-1_Amended_03202023.pdf"
    redirect_entry.redirect_link = "/files/documents/rule-1.pdf"
    redirect_entry.site = "localhost"
    redirect_entry.is_permanent = True

    mock_redirect_objects.filter.return_value.first.return_value = redirect_entry

    request = RequestFactory().get("/files/documents/Rule-1_Amended_03202023.pdf")

    # Act
    all_legacy_documents_redirect(request, "Rule-1_Amended_03202023.pdf")

    # Assert
    mock_render_404.assert_called_once_with(request)


@pytest.mark.django_db
@patch("wagtail.contrib.redirects.models.Redirect.objects")
def test_allows_database_redirect_to_safe_url(mock_redirect_objects):
    """Test that database redirects to URLs that won't cause loops are allowed"""
    # Arrange
    from types import SimpleNamespace

    # Mock a redirect to a safe URL (not handled by our function)
    redirect_entry = SimpleNamespace()
    redirect_entry.old_path = "/files/documents/old-file.pdf"
    redirect_entry.redirect_link = "/some/other/path/file.pdf"
    redirect_entry.site = "localhost"
    redirect_entry.is_permanent = True

    mock_redirect_objects.filter.return_value.first.return_value = redirect_entry

    request = RequestFactory().get("/files/documents/old-file.pdf")

    # Act
    response = all_legacy_documents_redirect(request, "old-file.pdf")

    # Assert
    assert response.status_code == 301  # HttpResponsePermanentRedirect
    assert response.url == "/some/other/path/file.pdf"


@pytest.mark.django_db
@patch("app.urls.render_404_util")
@patch("wagtail.contrib.redirects.models.Redirect.objects")
def test_exact_scenario_from_logs_rule_1_amended(
    mock_redirect_objects, mock_render_404
):
    """Test the exact scenario from the logs: Rule-1_Amended_03202023.pdf redirecting to rule-1.pdf"""
    # Arrange
    from types import SimpleNamespace

    # Mock the exact redirect from the logs
    redirect_entry = SimpleNamespace()
    redirect_entry.old_path = "/files/documents/Rule-1_Amended_03202023.pdf"
    redirect_entry.redirect_link = (
        "https://tbollu-sandbox-web.ustaxcourt.gov/files/documents/rule-1.pdf"
    )
    redirect_entry.site = "localhost"
    redirect_entry.is_permanent = True

    mock_redirect_objects.filter.return_value.first.return_value = redirect_entry

    request = RequestFactory().get("/files/documents/Rule-1_Amended_03202023.pdf")

    # Act
    all_legacy_documents_redirect(request, "Rule-1_Amended_03202023.pdf")

    # Assert
    # Should return 404 instead of redirect to prevent infinite loop
    mock_render_404.assert_called_once_with(request)


@pytest.mark.django_db
@patch("app.urls.render_404_util")
@patch("wagtail.contrib.redirects.models.Redirect.objects")
def test_complete_rules_scenario_from_logs(mock_redirect_objects, mock_render_404):
    """Test the Complete Rules scenario from logs that was working"""
    # Arrange
    from types import SimpleNamespace

    # Mock the redirect that should work (redirects to different pattern)
    redirect_entry = SimpleNamespace()
    redirect_entry.old_path = (
        "/files/documents/Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf"
    )
    redirect_entry.redirect_link = "/files/documents/complete-ropp.pdf"
    redirect_entry.site = "localhost"
    redirect_entry.is_permanent = True

    mock_redirect_objects.filter.return_value.first.return_value = redirect_entry

    request = RequestFactory().get(
        "/files/documents/Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf"
    )

    # Act
    all_legacy_documents_redirect(
        request, "Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf"
    )

    # Assert
    # This should still trigger the loop prevention since the target is also handled by this function
    mock_render_404.assert_called_once_with(request)
