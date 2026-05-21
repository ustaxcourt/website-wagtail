"""Tests for home/models/pages/definitions.py"""

from unittest.mock import patch, MagicMock


class TestDefinitionsPageGetContext:
    def _make_page(self):
        from home.models.pages.definitions import DefinitionsPage

        page = DefinitionsPage.__new__(DefinitionsPage)
        return page

    def _make_block(self, question):
        block = MagicMock()
        block.block_type = "definition"
        block.value = MagicMock()
        block.value.get = lambda k, default=None: {
            "question": question,
            "answer": "some answer",
        }.get(k, default)
        return block

    def test_empty_definitions_returns_empty_context(self):
        page = self._make_page()
        page.__dict__["definitions"] = []

        request = MagicMock()
        with patch("wagtail.models.Page.get_context", return_value={}):
            context = page.get_context(request)

        assert context["grouped_definitions"] == []
        assert context["available_letters"] == []
        assert context["available_words"] == []

    def test_single_definition_groups_by_letter(self):
        page = self._make_page()
        block = self._make_block("Apple")
        page.__dict__["definitions"] = [block]  # bypass descriptor

        request = MagicMock()
        with patch("wagtail.models.Page.get_context", return_value={}):
            context = page.get_context(request)

        assert len(context["grouped_definitions"]) == 1
        assert context["grouped_definitions"][0][0] == "A"
        assert context["available_letters"] == ["A"]
        assert "Apple" in context["available_words"]

    def test_multiple_definitions_sorted_alphabetically(self):
        page = self._make_page()
        blocks = [self._make_block("Banana"), self._make_block("Apple")]
        page.__dict__["definitions"] = blocks

        request = MagicMock()
        with patch("wagtail.models.Page.get_context", return_value={}):
            context = page.get_context(request)

        letters = [item[0] for item in context["grouped_definitions"]]
        assert "A" in letters
        assert "B" in letters

    def test_non_definition_block_is_skipped(self):
        page = self._make_page()
        block = MagicMock()
        block.block_type = "other_type"
        page.__dict__["definitions"] = [block]

        request = MagicMock()
        with patch("wagtail.models.Page.get_context", return_value={}):
            context = page.get_context(request)

        assert context["grouped_definitions"] == []

    def test_block_with_empty_question_is_skipped(self):
        page = self._make_page()
        block = MagicMock()
        block.block_type = "definition"
        block.value = MagicMock()
        block.value.get = lambda k, default=None: {
            "question": "",
            "answer": "some answer",
        }.get(k, default)
        page.__dict__["definitions"] = [block]

        request = MagicMock()
        with patch("wagtail.models.Page.get_context", return_value={}):
            context = page.get_context(request)

        assert context["grouped_definitions"] == []


class TestDefinitionsPageGetWordList:
    def test_returns_list_of_questions(self):
        from home.models.pages.definitions import DefinitionsPage

        mock_page = MagicMock()
        mock_page.definitions.get_prep_value.return_value = [
            {"type": "definition", "value": {"question": "  Alpha  "}},
            {"type": "definition", "value": {"question": "Beta"}},
        ]

        with patch.object(DefinitionsPage.objects, "first", return_value=mock_page):
            result = DefinitionsPage.getWordList()

        assert "alpha" in result
        assert "beta" in result

    def test_skips_blocks_without_question(self):
        from home.models.pages.definitions import DefinitionsPage

        mock_page = MagicMock()
        mock_page.definitions.get_prep_value.return_value = [
            {"type": "definition", "value": {}},
            {"type": "definition", "value": {"question": "Gamma"}},
        ]

        with patch.object(DefinitionsPage.objects, "first", return_value=mock_page):
            result = DefinitionsPage.getWordList()

        assert result == ["gamma"]

    def test_skips_blocks_without_value(self):
        from home.models.pages.definitions import DefinitionsPage

        mock_page = MagicMock()
        mock_page.definitions.get_prep_value.return_value = [
            {"type": "definition"},
        ]

        with patch.object(DefinitionsPage.objects, "first", return_value=mock_page):
            result = DefinitionsPage.getWordList()

        assert result == []
