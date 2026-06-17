"""Tests for home/admin/moderation.py"""

from wagtail.admin.panels import FieldPanel, PublishingPanel, TabbedInterface


class FakeSnippetModel:
    content_panels = [FieldPanel("title")]


class FakeSnippetModelWithNote:
    content_panels = [FieldPanel("title")]
    note = None


class FakeModelWithPanels:
    panels = [FieldPanel("title")]


class FakeModelNoPanels:
    pass


class TestGetModerationEditHandlerSimple:
    def test_with_model_having_content_panels(self):
        from home.admin.moderation import get_moderation_edit_handler_simple

        result = get_moderation_edit_handler_simple(FakeSnippetModel)
        assert isinstance(result, list)
        field_names = [p.field_name for p in result if isinstance(p, FieldPanel)]
        assert "review_by" in field_names

    def test_with_model_having_panels_attribute(self):
        from home.admin.moderation import get_moderation_edit_handler_simple

        result = get_moderation_edit_handler_simple(FakeModelWithPanels)
        assert isinstance(result, list)
        field_names = [p.field_name for p in result if isinstance(p, FieldPanel)]
        assert "review_by" in field_names

    def test_fallback_when_model_has_no_panels_starts_with_empty_content(self):
        """With no panels to copy, the result should contain only review_by and PublishingPanel."""
        from home.admin.moderation import get_moderation_edit_handler_simple

        result = get_moderation_edit_handler_simple(FakeModelNoPanels)
        field_names = [p.field_name for p in result if isinstance(p, FieldPanel)]
        assert field_names == ["review_by"]
        assert any(isinstance(p, PublishingPanel) for p in result)

    def test_with_explicit_content_panels(self):
        """if content_panels are explicitly provided, they should appear and review_by should be added."""
        from home.admin.moderation import get_moderation_edit_handler_simple

        panels = [FieldPanel("title")]
        result = get_moderation_edit_handler_simple(
            FakeSnippetModel, content_panels=panels
        )
        assert isinstance(result, list)
        field_names = [p.field_name for p in result if isinstance(p, FieldPanel)]
        assert "review_by" in field_names

    def test_model_with_note_attr_adds_note_panel(self):
        """if the model has a note attribute, a note panel should be added."""
        from home.admin.moderation import get_moderation_edit_handler_simple

        result = get_moderation_edit_handler_simple(FakeSnippetModelWithNote)
        field_names = [p.field_name for p in result if isinstance(p, FieldPanel)]
        assert "note" in field_names

    def test_publishing_panel_is_last(self):
        """PublishingPanel should always be the final panel in the list."""
        from home.admin.moderation import get_moderation_edit_handler_simple

        result = get_moderation_edit_handler_simple(FakeSnippetModel)
        assert isinstance(result[-1], PublishingPanel)

    def test_with_wagtail_page_model_adds_review_by(self):
        """Page has its own content_panels, so review_by should be appended to them."""
        from home.admin.moderation import get_moderation_edit_handler_simple
        from wagtail.models import Page

        result = get_moderation_edit_handler_simple(Page)
        field_names = [p.field_name for p in result if isinstance(p, FieldPanel)]
        assert "review_by" in field_names


class TestModerationTabbedInterfaceCreateForModel:
    def test_returns_tabbed_interface_for_snippet(self):
        from home.admin.moderation import ModerationTabbedInterface

        result = ModerationTabbedInterface.create_for_model(FakeSnippetModel)
        assert isinstance(result, TabbedInterface)

    def test_returns_tabbed_interface_for_page_model(self):
        from home.admin.moderation import ModerationTabbedInterface
        from wagtail.models import Page

        result = ModerationTabbedInterface.create_for_model(Page)
        assert isinstance(result, TabbedInterface)

    def test_with_explicit_content_panels_for_snippet(self):
        from home.admin.moderation import ModerationTabbedInterface

        result = ModerationTabbedInterface.create_for_model(
            FakeSnippetModel, content_panels=[FieldPanel("title")]
        )
        assert isinstance(result, TabbedInterface)

    def test_with_page_model_and_explicit_promote_panels(self):
        from home.admin.moderation import ModerationTabbedInterface
        from wagtail.models import Page

        result = ModerationTabbedInterface.create_for_model(
            Page,
            content_panels=[FieldPanel("title")],
            promote_panels=[FieldPanel("slug")],
            settings_panels=[],
        )
        assert isinstance(result, TabbedInterface)

    def test_with_model_having_note_attribute(self):
        from home.admin.moderation import ModerationTabbedInterface

        result = ModerationTabbedInterface.create_for_model(FakeSnippetModelWithNote)
        assert isinstance(result, TabbedInterface)

    def test_with_none_model_class_and_explicit_panels(self):
        from home.admin.moderation import ModerationTabbedInterface

        result = ModerationTabbedInterface.create_for_model(
            None, content_panels=[FieldPanel("title")]
        )
        assert isinstance(result, TabbedInterface)

    def test_snippet_model_without_content_panels_still_gets_moderation_tab(self):
        """Even with no content panels, the moderation tab (with review_by) should be built."""
        from home.admin.moderation import ModerationTabbedInterface

        result = ModerationTabbedInterface.create_for_model(FakeModelNoPanels)
        assert isinstance(result, TabbedInterface)
        tab_headings = [tab.heading for tab in result.children]
        assert "Moderation" in tab_headings

    def test_page_model_with_empty_promote_panels_skips_tab(self):
        from home.admin.moderation import ModerationTabbedInterface
        from wagtail.models import Page

        result = ModerationTabbedInterface.create_for_model(
            Page,
            content_panels=[FieldPanel("title")],
            promote_panels=[],
            settings_panels=[],
        )
        assert isinstance(result, TabbedInterface)


class TestModerationTabbedInterfaceCreateForPage:
    def test_with_explicit_panels(self):
        from home.admin.moderation import ModerationTabbedInterface

        result = ModerationTabbedInterface.create_for_page(
            content_panels=[FieldPanel("title")],
            promote_panels=[FieldPanel("slug")],
            settings_panels=[],
        )
        assert isinstance(result, TabbedInterface)

    def test_with_no_optional_panels_uses_page_defaults(self):
        from home.admin.moderation import ModerationTabbedInterface

        result = ModerationTabbedInterface.create_for_page(
            content_panels=[FieldPanel("title")],
        )
        assert isinstance(result, TabbedInterface)

    def test_with_none_promote_panels_falls_back_to_page_defaults(self):
        from home.admin.moderation import ModerationTabbedInterface

        result = ModerationTabbedInterface.create_for_page(
            content_panels=[FieldPanel("title")],
            promote_panels=None,
        )
        assert isinstance(result, TabbedInterface)


class TestModerationEditHandlerDecorator:
    def test_decorator_sets_edit_handler(self):
        from home.admin.moderation import moderation_edit_handler

        @moderation_edit_handler()
        class FakeModel:
            content_panels = [FieldPanel("title")]

        assert hasattr(FakeModel, "edit_handler")
        assert isinstance(FakeModel.edit_handler, TabbedInterface)

    def test_decorator_returns_class_unchanged_otherwise(self):
        from home.admin.moderation import moderation_edit_handler

        @moderation_edit_handler()
        class FakeModel:
            content_panels = [FieldPanel("title")]
            some_attr = "value"

        assert FakeModel.some_attr == "value"
        assert FakeModel.__name__ == "FakeModel"

    def test_decorator_with_explicit_panels(self):
        from home.admin.moderation import moderation_edit_handler

        @moderation_edit_handler(content_panels=[FieldPanel("title")])
        class FakeModel:
            pass

        assert hasattr(FakeModel, "edit_handler")


class TestModerationAdminMixinGetPanels:
    def test_get_panels_returns_list(self):
        from home.admin.moderation import ModerationAdminMixin

        class FakeAdmin(ModerationAdminMixin):
            content_panels = [FieldPanel("title")]

        result = FakeAdmin.get_panels()
        assert isinstance(result, list)
        assert len(result) > 0
