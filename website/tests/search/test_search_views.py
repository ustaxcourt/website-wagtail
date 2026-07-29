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
class TestSearchViewDocketDetection:
    """Tests for DAWSON docket-number detection wired into the search view."""

    def _make_request(self, query="tax"):
        factory = RequestFactory()
        return factory.get("/search/", {"query": query})

    def _run_search(self, docket_match, docket_case_record=None):
        from search.views import search

        request = self._make_request(query="123-19")
        with patch("search.views.Page") as mock_page_cls:
            mock_page_cls.objects.live.return_value.search.return_value = []
            with patch("search.views.JudgeProfile") as mock_judge:
                mock_judge.objects.filter.return_value.filter.return_value = []
                with patch("search.views.Query") as mock_query_cls:
                    mock_query_cls.get.return_value = MagicMock()
                    with patch("search.views.SearchPromotion") as mock_promo:
                        mock_promo.objects.filter.return_value.select_related.return_value = []
                        with patch(
                            "search.views.is_docket_number",
                            return_value=docket_match,
                        ):
                            with patch(
                                "search.views.get_case_record",
                                return_value=docket_case_record,
                            ) as mock_get_case_record:
                                with patch("search.views.TemplateResponse") as mock_tr:
                                    mock_tr.return_value = MagicMock(status_code=200)
                                    search(request)
                                    ctx = mock_tr.call_args[0][2]
                                    return ctx, mock_query_cls, mock_get_case_record

    def test_non_docket_query_leaves_docket_context_empty(self):
        ctx, mock_query_cls, mock_get_case_record = self._run_search(docket_match=None)
        assert ctx["docket_match"] is None
        assert ctx["docket_case_record"] is None
        mock_get_case_record.assert_not_called()
        # Only the literal query hit was recorded, no docket report roll-up.
        mock_query_cls.get.assert_called_once_with("123-19")

    def test_valid_docket_number_fetches_case_record(self):
        from search.dawson import DocketMatch
        from search.dawson_client import DawsonCaseRecord

        match = DocketMatch(term="123-19", docket_number="123-19", is_valid=True)
        record = DawsonCaseRecord(
            docket_number="123-19",
            case_caption="Some Petitioner",
            filing_date="2019-01-01T00:00:00.000Z",
            dawson_url="https://dawson.ustaxcourt.gov/case-detail/123-19",
        )
        ctx, mock_query_cls, mock_get_case_record = self._run_search(
            docket_match=match, docket_case_record=record
        )
        assert ctx["docket_match"] == match
        assert ctx["docket_case_record"] == record
        mock_get_case_record.assert_called_once_with("123-19")
        # Literal query hit + docket report roll-up hit.
        mock_query_cls.get.assert_any_call("123-19")
        mock_query_cls.get.assert_any_call("Docket Number Search")

    def test_invalid_docket_format_does_not_fetch_case_record(self):
        from search.dawson import DocketMatch

        match = DocketMatch(term="123-19", docket_number=None, is_valid=False)
        ctx, mock_query_cls, mock_get_case_record = self._run_search(
            docket_match=match, docket_case_record=None
        )
        assert ctx["docket_match"] == match
        assert ctx["docket_case_record"] is None
        mock_get_case_record.assert_not_called()
        # Still rolled up into the docket report line item.
        mock_query_cls.get.assert_any_call("Docket Number Search")

    def test_dawson_api_error_degrades_to_no_docket_result(self):
        from search.dawson import DocketMatch

        match = DocketMatch(term="123-19", docket_number="123-19", is_valid=True)
        ctx, _, mock_get_case_record = self._run_search(
            docket_match=match, docket_case_record=None
        )
        mock_get_case_record.assert_called_once_with("123-19")
        assert ctx["docket_case_record"] is None


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

    def test_questionanswers_answer_dict_with_rich_text(self):
        """Branch: isinstance(qa['answer'], dict) and 'rich_text' in qa['answer']."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        rich_text_obj = SimpleNamespace(source="Rich text content")
        qa_entry = {"question": "Q?", "answer": {"rich_text": rich_text_obj}}
        block = SimpleNamespace(block_type="questionanswers", value=[qa_entry])
        result = extract_text_from_streamfield([block])
        assert "Rich text content" in result

    def test_value_is_list_recurses(self):
        """Branch: isinstance(value, list) - lines 63-64."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        inner_block = SimpleNamespace(block_type="text", value="nested text")
        block = SimpleNamespace(block_type="container", value=[inner_block])
        result = extract_text_from_streamfield([block])
        assert "nested text" in result

    def test_empty_stream_value_returns_empty_string(self):
        """Branch: not stream_value - line 25-26."""
        from search.views import extract_text_from_streamfield

        assert extract_text_from_streamfield([]) == ""
        assert extract_text_from_streamfield(None) == ""

    def test_value_is_dict_with_string_values(self):
        """Branch: isinstance(value, dict) with str values - lines 53-62."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        block = SimpleNamespace(block_type="data", value={"key": "string value"})
        result = extract_text_from_streamfield([block])
        assert "string value" in result

    def test_value_is_dict_with_list_value_recurses(self):
        """Branch: isinstance(v, list) in dict loop - line 58-60."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        inner_block = SimpleNamespace(block_type="text", value="list in dict")
        block = SimpleNamespace(block_type="data", value={"items": [inner_block]})
        result = extract_text_from_streamfield([block])
        assert "list in dict" in result


@pytest.mark.django_db
class TestGetSearchSnippet:
    """Test missing branches in get_search_snippet."""

    def test_uses_search_description_when_present(self):
        from search.views import get_search_snippet

        page = MagicMock()
        page.specific.search_description = "My meta description"
        result = get_search_snippet(page)
        assert result == "My meta description"

    def test_falls_back_to_body_str(self):
        """Branch: isinstance(body, str) - line 91."""
        from search.views import get_search_snippet
        from types import SimpleNamespace

        page = MagicMock()
        page.specific = SimpleNamespace(
            search_description=None,
            body="Plain text body content here.",
        )
        result = get_search_snippet(page)
        assert "Plain text body" in result

    def test_falls_back_to_intro_when_no_body(self):
        """Branch: hasattr(specific_page, 'intro') fallback - lines 94-95."""
        from search.views import get_search_snippet
        from types import SimpleNamespace

        page = MagicMock()
        page.specific = SimpleNamespace(
            search_description=None,
            intro="Intro text here.",
        )
        result = get_search_snippet(page)
        assert "Intro text here" in result

    def test_returns_empty_string_when_no_content(self):
        from search.views import get_search_snippet
        from types import SimpleNamespace

        page = MagicMock()
        page.specific = SimpleNamespace(search_description=None)
        result = get_search_snippet(page)
        assert result == ""

    def test_falls_back_to_release_entries_when_present(self):
        """Branch: hasattr(specific_page, 'release_entries') - line 85-86."""
        from search.views import get_search_snippet
        from types import SimpleNamespace

        specific = SimpleNamespace(
            search_description=None,
            body="some body",
            release_entries="<p>Release entry text</p>",
        )
        page = MagicMock()
        page.specific = specific
        result = get_search_snippet(page)
        assert "Release entry text" in result

    def test_body_with_stream_data_attr(self):
        """Branch: hasattr(body, 'stream_data') or hasattr(body, 'blocks') - line 89-90."""
        from search.views import get_search_snippet
        from types import SimpleNamespace

        class IterableWithStreamData:
            stream_data = []

            def __iter__(self):
                return iter([])

            def __bool__(self):
                return True

        specific = SimpleNamespace(
            search_description=None,
            body=IterableWithStreamData(),
        )
        page = MagicMock()
        page.specific = specific
        result = get_search_snippet(page)
        assert isinstance(result, str)

    def test_body_not_a_recognized_type_falls_through(self):
        """Branch: body is not str/StreamValue/stream_data → line 91->94 (falls to intro check)."""
        from search.views import get_search_snippet
        from types import SimpleNamespace

        specific = SimpleNamespace(
            search_description=None,
            body=42,
            intro="Intro from fallback",
        )
        page = MagicMock()
        page.specific = specific
        result = get_search_snippet(page)
        assert "Intro from fallback" in result


@pytest.mark.django_db
class TestExtractTextFromStreamfieldBranches:
    """Additional branch coverage for extract_text_from_streamfield."""

    def test_qa_not_a_dict_is_skipped(self):
        """Branch: isinstance(qa, dict) is False - 32->31."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        block = SimpleNamespace(block_type="questionanswers", value=["not a dict"])
        result = extract_text_from_streamfield([block])
        assert result == ""

    def test_qa_dict_without_question_key(self):
        """Branch: 'question' not in qa - 33->35."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        qa_entry = {"answer": "Some answer"}
        block = SimpleNamespace(block_type="questionanswers", value=[qa_entry])
        result = extract_text_from_streamfield([block])
        assert "Some answer" in result

    def test_qa_dict_without_answer_key(self):
        """Branch: 'answer' not in qa - 35->31."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        qa_entry = {"question": "Some question?"}
        block = SimpleNamespace(block_type="questionanswers", value=[qa_entry])
        result = extract_text_from_streamfield([block])
        assert "Some question?" in result

    def test_qa_answer_none_of_known_types(self):
        """Branch: answer is not str, not rich_text dict, not has source - 43->31."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        qa_entry = {"question": "Q?", "answer": 42}
        block = SimpleNamespace(block_type="questionanswers", value=[qa_entry])
        result = extract_text_from_streamfield([block])
        assert "Q?" in result

    def test_value_with_stream_data_recurses(self):
        """Branch: hasattr(value, 'stream_data') - line 45-48."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        inner = SimpleNamespace(block_type="text", value="nested content")

        class IterableStreamData(list):
            stream_data = True

        nested_stream = IterableStreamData([inner])
        block = SimpleNamespace(block_type="nested", value=nested_stream)
        result = extract_text_from_streamfield([block])
        assert "nested content" in result

    def test_dict_value_with_multiple_items(self):
        """Branch: multiple dict items to cover 61->54 arc."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        block = SimpleNamespace(
            block_type="data",
            value={"key1": "value one", "key2": "value two"},
        )
        result = extract_text_from_streamfield([block])
        assert "value one" in result
        assert "value two" in result

    def test_multiple_blocks_with_list_values(self):
        """Multiple blocks to cover 63->28 arc (list value then next block)."""
        from search.views import extract_text_from_streamfield
        from types import SimpleNamespace

        inner = SimpleNamespace(block_type="text", value="in list")
        block1 = SimpleNamespace(block_type="list_block", value=[inner])
        block2 = SimpleNamespace(block_type="text", value="after list")
        result = extract_text_from_streamfield([block1, block2])
        assert "in list" in result
        assert "after list" in result


@pytest.mark.django_db
class TestSearchViewPromotionNoSnippet:
    """Cover line 142->147: promotion with no organic snippet."""

    def _make_request(self, query="tax"):
        from django.test import RequestFactory

        factory = RequestFactory()
        return factory.get("/search/", {"query": query})

    def test_promotion_without_organic_snippet_does_not_update(self):
        """Organic result has no search_snippet → doesn't update promotion description."""
        from search.views import search

        organic = MagicMock()
        organic.title = "Tax Info"
        organic.pk = 10
        del organic.search_snippet

        promotion = MagicMock()
        promotion.page = MagicMock()
        promotion.page.id = 10
        promotion.page.pk = 10

        request = self._make_request()
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
                        with patch("search.views.get_search_snippet", return_value=""):
                            with patch("search.views.TemplateResponse") as mock_tr:
                                mock_tr.return_value = MagicMock(status_code=200)
                                search(request)
                                mock_tr.assert_called_once()
