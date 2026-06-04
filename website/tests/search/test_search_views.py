"""Tests for search/views.py — search and definitions_search views."""

import json
import pytest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory


@pytest.mark.django_db
class TestSearchView:
    def _make_request(self, query=None, page=None):
        factory = RequestFactory()
        params = {}
        if query is not None:
            params["query"] = query
        if page is not None:
            params["page"] = page
        return factory.get("/search/", params)

    def test_search_no_query_returns_empty(self):
        from search.views import search

        request = self._make_request()
        mock_pages = MagicMock()
        mock_pages.none.return_value = []
        with patch("search.views.Page") as mock_page_cls:
            mock_page_cls.objects.none.return_value = []
            with patch("search.views.SearchPromotion") as mock_promo:
                mock_promo.objects.none.return_value = []
                with patch("search.views.TemplateResponse") as mock_tr:
                    mock_tr.return_value = MagicMock(status_code=200)
                    search(request)
                    mock_tr.assert_called_once()
                    ctx = mock_tr.call_args[0][2]
                    assert ctx["search_query"] is None

    def test_search_with_query_calls_live_search(self):
        from search.views import search

        request = self._make_request(query="tax court")

        mock_result = MagicMock()
        mock_result.title = "Tax Court Rules"
        mock_result.pk = 1

        with patch("search.views.Page") as mock_page_cls:
            mock_page_cls.objects.live.return_value.search.return_value = [mock_result]
            with patch("search.views.JudgeProfile") as mock_judge:
                mock_judge.objects.filter.return_value.filter.return_value = []
                with patch("search.views.Query") as mock_query_cls:
                    mock_q = MagicMock()
                    mock_query_cls.get.return_value = mock_q
                    with patch("search.views.SearchPromotion") as mock_promo:
                        mock_promo.objects.filter.return_value.select_related.return_value = []
                        with patch(
                            "search.views.get_search_snippet", return_value="snippet"
                        ):
                            with patch("search.views.TemplateResponse") as mock_tr:
                                mock_tr.return_value = MagicMock(status_code=200)
                                search(request)
                                mock_q.add_hit.assert_called_once()

    def test_search_excludes_press_releases(self):
        from search.views import search

        request = self._make_request(query="news")

        excluded = MagicMock()
        excluded.title = "Press Releases & News"
        excluded.pk = 2

        included = MagicMock()
        included.title = "Some Other Page"
        included.pk = 3

        with patch("search.views.Page") as mock_page_cls:
            mock_page_cls.objects.live.return_value.search.return_value = [
                excluded,
                included,
            ]
            with patch("search.views.JudgeProfile") as mock_judge:
                mock_judge.objects.filter.return_value.filter.return_value = []
                with patch("search.views.Query") as mock_query_cls:
                    mock_query_cls.get.return_value = MagicMock()
                    with patch("search.views.SearchPromotion") as mock_promo:
                        mock_promo.objects.filter.return_value.select_related.return_value = []
                        with patch("search.views.get_search_snippet", return_value=""):
                            with patch("search.views.TemplateResponse") as mock_tr:
                                mock_tr.return_value = MagicMock(status_code=200)
                                search(request)
                                ctx = mock_tr.call_args[0][2]
                                result_titles = [
                                    r.title for r in ctx["search_results"].object_list
                                ]
                                assert "Press Releases & News" not in result_titles

    def test_search_pagination_invalid_page(self):
        from search.views import search

        request = self._make_request(query="rule", page="invalid")

        with patch("search.views.Page") as mock_page_cls:
            mock_page_cls.objects.live.return_value.search.return_value = []
            with patch("search.views.JudgeProfile") as mock_judge:
                mock_judge.objects.filter.return_value.filter.return_value = []
                with patch("search.views.Query") as mock_query_cls:
                    mock_query_cls.get.return_value = MagicMock()
                    with patch("search.views.SearchPromotion") as mock_promo:
                        mock_promo.objects.filter.return_value.select_related.return_value = []
                        with patch("search.views.TemplateResponse") as mock_tr:
                            mock_tr.return_value = MagicMock(status_code=200)
                            search(request)
                            mock_tr.assert_called_once()

    def test_search_with_judge_results(self):
        from search.views import search

        request = self._make_request(query="judge name")

        judge = MagicMock()
        judge.display_name = "Judge Smith"
        judge.first_name = "John"
        judge.last_name = "Smith"
        judge.id = 5

        with patch("search.views.Page") as mock_page_cls:
            mock_page_cls.objects.live.return_value.search.return_value = []
            with patch("search.views.JudgeProfile") as mock_judge:
                mock_judge.objects.filter.return_value.filter.return_value = [judge]
                with patch("search.views.Query") as mock_query_cls:
                    mock_query_cls.get.return_value = MagicMock()
                    with patch("search.views.SearchPromotion") as mock_promo:
                        mock_promo.objects.filter.return_value.select_related.return_value = []
                        with patch("search.views.TemplateResponse") as mock_tr:
                            mock_tr.return_value = MagicMock(status_code=200)
                            search(request)
                            ctx = mock_tr.call_args[0][2]
                            # Judge should be in results
                            results = ctx["search_results"].object_list
                            assert any("Smith" in r.title for r in results)


@pytest.mark.django_db
class TestDefinitionsSearchView:
    def test_definitions_search_returns_200(self):
        from search.views import definitions_search

        factory = RequestFactory()
        body = json.dumps({"definitions-query": "petitioner"})
        request = factory.post(
            "/definitions-search/", data=body, content_type="application/json"
        )

        with patch("search.views.DefinitionsQuery") as mock_dq:
            mock_q = MagicMock()
            mock_dq.get.return_value = mock_q
            response = definitions_search(request)
            assert response.status_code == 200
            mock_q.add_hit.assert_called_once()

    def test_definitions_search_missing_key_uses_default(self):
        from search.views import definitions_search

        factory = RequestFactory()
        body = json.dumps({})  # no "definitions-query" key
        request = factory.post(
            "/definitions-search/", data=body, content_type="application/json"
        )

        with patch("search.views.DefinitionsQuery") as mock_dq:
            mock_dq.get.return_value = MagicMock()
            response = definitions_search(request)
            assert response.status_code == 200
            mock_dq.get.assert_called_with("error_A")


@pytest.mark.django_db
class TestSearchViewPromotions:
    """Tests for search promotions handling (lines 136-147, 181-182)."""

    def _make_request(self, query=None, page=None):
        factory = RequestFactory()
        params = {}
        if query is not None:
            params["query"] = query
        if page is not None:
            params["page"] = page
        return factory.get("/search/", params)

    def test_search_with_promotion_matching_organic_result(self):
        """Promotion matching organic result updates description."""
        from search.views import search

        organic = MagicMock()
        organic.title = "Tax Info"
        organic.pk = 10
        organic.search_snippet = "organic snippet"

        promotion = MagicMock()
        promotion.page = MagicMock()
        promotion.page.id = 10
        promotion.page.pk = 10

        request = self._make_request(query="tax")
        with patch("search.views.Page") as mock_page_cls:
            mock_page_cls.objects.live.return_value.search.return_value = [organic]
            with patch("search.views.JudgeProfile") as mock_judge:
                mock_judge.objects.filter.return_value.filter.return_value = []
                with patch("search.views.Query") as mock_query_cls:
                    mock_query_cls.get.return_value = MagicMock()
                    with patch("search.views.SearchPromotion") as mock_promo:
                        mock_promo.objects.filter.return_value.select_related.return_value = [
                            promotion
                        ]
                        with patch(
                            "search.views.get_search_snippet",
                            return_value="organic snippet",
                        ):
                            with patch("search.views.TemplateResponse") as mock_tr:
                                mock_tr.return_value = MagicMock(status_code=200)
                                search(request)
                                # promotion description should have been updated
                                assert promotion.description == "organic snippet"

    def test_search_empty_page_returns_last_page(self):
        """EmptyPage exception falls back to last page."""
        from search.views import search

        request = self._make_request(query="tax", page="999")
        with patch("search.views.Page") as mock_page_cls:
            mock_page_cls.objects.live.return_value.search.return_value = []
            with patch("search.views.JudgeProfile") as mock_judge:
                mock_judge.objects.filter.return_value.filter.return_value = []
                with patch("search.views.Query") as mock_query_cls:
                    mock_query_cls.get.return_value = MagicMock()
                    with patch("search.views.SearchPromotion") as mock_promo:
                        mock_promo.objects.filter.return_value.select_related.return_value = []
                        with patch("search.views.TemplateResponse") as mock_tr:
                            mock_tr.return_value = MagicMock(status_code=200)
                            search(request)
                            mock_tr.assert_called_once()


@pytest.mark.django_db
class TestExtractTextFromStreamfieldSearch:
    """Test missing branches in search/views.py extract_text_from_streamfield."""

    def test_questionanswers_string_answer(self):
        """Branch: isinstance(qa['answer'], str) - line 43-44."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        qa_entry = {"question": "Q?", "answer": "String answer"}
        block = SimpleNamespace(block_type="questionanswers", value=[qa_entry])
        result = extract_text_from_streamfield([block])
        assert "String answer" in result

    def test_questionanswers_answer_with_source(self):
        """Branch: hasattr(qa['answer'], 'source') - line 48."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        answer_obj = SimpleNamespace(source="Source answer text")
        qa_entry = {"question": "Q?", "answer": answer_obj}
        block = SimpleNamespace(block_type="questionanswers", value=[qa_entry])
        result = extract_text_from_streamfield([block])
        assert "Source answer text" in result
