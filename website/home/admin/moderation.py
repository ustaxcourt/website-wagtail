from wagtail.admin.panels import (
    ObjectList,
    TabbedInterface,
    FieldPanel,
    PublishingPanel,
)
from wagtail.admin.widgets import AdminDateTimeInput
from wagtail.models.panels import PanelPlaceholder


def _contains_publishing_panel(panels):
    """
    Return True if any panel in ``panels`` (searched recursively) is a PublishingPanel.

    Wagtail's default ``Page.settings_panels`` holds a lazy ``PanelPlaceholder``
    for PublishingPanel rather than an instance, so placeholders are checked too.

    PublishingPanel must appear at most once per edit form: each one renders the
    ``go_live_at``/``expire_at`` inputs and the ``#schedule-publishing-dialog``
    markup, and duplicate DOM ids break the jQuery datetimepicker (which binds by
    ``#id``), leaving the "Set schedule" calendar blank (WAG-1433).
    """
    for panel in panels or []:
        if isinstance(panel, PublishingPanel):
            return True
        if isinstance(panel, PanelPlaceholder) and issubclass(
            panel.panel_class, PublishingPanel
        ):
            return True
        if _contains_publishing_panel(getattr(panel, "children", None)):
            return True
    return False


def _build_moderation_tab(include_note, other_panels):
    """
    Build the Moderation tab. A PublishingPanel is only added when none of
    ``other_panels`` already provides one, so the form never renders two.
    """
    moderation_panels = [FieldPanel("review_by", widget=AdminDateTimeInput())]
    if include_note:
        moderation_panels.append(FieldPanel("note"))
    if not _contains_publishing_panel(other_panels):
        moderation_panels.append(PublishingPanel())
    return ObjectList(moderation_panels, heading="Moderation")


def get_moderation_edit_handler_simple(model_class, content_panels=None):
    """
    Simple factory function that adds review_by field to existing panels without complex tabs.
    This approach is more compatible with Wagtail's admin checks.

    Args:
        model_class: The model class
        content_panels: List of panels for content (if None, uses model's content_panels or panels)

    Returns:
        Updated panels list with moderation fields
    """
    from wagtail.models import Page

    # Determine if this is a page or snippet model
    is_page_model = issubclass(model_class, Page)

    # Get content panels
    if content_panels is None:
        if hasattr(model_class, "content_panels"):
            content_panels = model_class.content_panels.copy()
        elif hasattr(model_class, "panels"):
            content_panels = model_class.panels.copy()
        else:
            # Fallback minimal panels
            content_panels = [FieldPanel("title")] if is_page_model else []
    else:
        content_panels = content_panels.copy()

    # Add review_by field before PublishingPanel
    content_panels.append(FieldPanel("review_by", widget=AdminDateTimeInput()))
    if hasattr(model_class, "note"):
        content_panels.append(FieldPanel("note"))
    if not _contains_publishing_panel(content_panels):
        content_panels.append(PublishingPanel())

    return content_panels


class ModerationTabbedInterface:
    """
    Custom tabbed interface that adds a dedicated moderation tab.
    """

    @classmethod
    def create_for_model(
        cls, model_class, content_panels=None, promote_panels=None, settings_panels=None
    ):
        """
        Create a TabbedInterface with moderation support for both pages and snippets.

        Args:
            model_class: The model class
            content_panels: List of panels for content tab
            promote_panels: List of panels for promote tab (page models only)
            settings_panels: List of panels for settings tab (page models only)
        """
        from wagtail.models import Page

        is_page_model = model_class and issubclass(model_class, Page)

        # Content tab
        if content_panels is None:
            if model_class and hasattr(model_class, "content_panels"):
                content_panels = model_class.content_panels
            else:
                content_panels = [FieldPanel("title")] if is_page_model else []

        content_tab = ObjectList(content_panels, heading="Content")

        # Resolve page-specific tabs first so the Moderation tab can skip its
        # PublishingPanel when the Settings tab already has Wagtail's default one.
        page_tabs = []
        if is_page_model:
            if promote_panels is None:
                promote_panels = getattr(
                    model_class, "promote_panels", Page.promote_panels
                )
            if promote_panels:
                page_tabs.append(ObjectList(promote_panels, heading="Promote"))

            if settings_panels is None:
                settings_panels = getattr(
                    model_class, "settings_panels", Page.settings_panels
                )
            if settings_panels:
                page_tabs.append(ObjectList(settings_panels, heading="Settings"))

        moderation_tab = _build_moderation_tab(
            include_note=hasattr(model_class, "note"),
            other_panels=[content_tab, *page_tabs],
        )

        return TabbedInterface([content_tab, moderation_tab, *page_tabs])

    @classmethod
    def create_for_snippet(cls, content_panels):
        """
        Create a TabbedInterface specifically for snippet models.
        """
        content_tab = ObjectList(content_panels, heading="Content")
        moderation_tab = _build_moderation_tab(
            include_note=True, other_panels=[content_tab]
        )

        return TabbedInterface([content_tab, moderation_tab])

    @classmethod
    def create_for_page(cls, content_panels, promote_panels=None, settings_panels=None):
        """
        Create a TabbedInterface specifically for page models.
        """
        from wagtail.models import Page

        content_tab = ObjectList(content_panels, heading="Content")

        if promote_panels is None:
            promote_panels = Page.promote_panels
        if settings_panels is None:
            settings_panels = Page.settings_panels
        promote_tab = ObjectList(promote_panels, heading="Promote")
        settings_tab = ObjectList(settings_panels, heading="Settings")

        moderation_tab = _build_moderation_tab(
            include_note=True,
            other_panels=[content_tab, promote_tab, settings_tab],
        )

        return TabbedInterface([content_tab, moderation_tab, promote_tab, settings_tab])


def moderation_edit_handler(
    content_panels=None, promote_panels=None, settings_panels=None
):
    """
    Decorator factory to create a moderation-enabled tabbed interface.

    Usage:
        @moderation_edit_handler()
        class MyModel(ModerationMixin, WorkflowMixin, ...):
            ...
    """

    def decorator(cls):
        cls.edit_handler = ModerationTabbedInterface.create_for_model(
            cls, content_panels, promote_panels, settings_panels
        )
        return cls

    return decorator


class ModerationAdminMixin:
    """
    Mixin for models that use the moderation system.
    Provides enhanced panels with moderation fields integrated.
    """

    @classmethod
    def get_panels(cls):
        """Return the panels with moderation fields integrated."""
        return get_moderation_edit_handler_simple(cls)
