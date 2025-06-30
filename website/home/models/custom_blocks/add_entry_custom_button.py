from django.utils.safestring import mark_safe
from wagtail.admin.panels import Panel
from django.urls import reverse


class AddEntryButton(Panel):
    def __init__(self, button_text="Run Step Action", **kwargs):
        super().__init__(**kwargs)
        self.button_text = button_text

    def clone(self):
        return self.__class__(button_text=self.button_text)

    class BoundPanel(Panel.BoundPanel):
        def __init__(self, panel, instance=None, form=None, request=None, prefix=None):
            super().__init__(
                panel=panel,
                instance=instance,
                form=form,
                request=request,
                prefix=prefix,
            )
            self.button_text = panel.button_text

        def render_html(self, parent_context=None):
            # Get the entry ID from the parent instance if available
            sort_order = getattr(self.instance, "sort_order", None)
            page_id = self.instance.homepage.id

            button_html = f"""
                <div style="margin-top:10px;">
                    <button type="button" class="step-action-btn">{self.button_text}</button>
                </div>
            """

            if sort_order is not None and page_id is not None:
                # If we have an entry ID and it's part of a homepage, we can create a proper link
                url = reverse("add_entry_above_view", args=[page_id, sort_order])
                button_html = f"""
                    <div style="margin-top:10px; margin-bottom:20px;">
                        <a href="{url}" class="button button-small button-secondary">{self.button_text}</a>
                    </div>
                """

            return mark_safe(button_html)
