from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from django.utils.html import strip_tags


class StandardPage(Page):
    class Meta:
        abstract = False

    body = RichTextField(blank=True, help_text="Insert text here.")

    content_panels = Page.content_panels + [FieldPanel("body")]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    @property
    def search_snippet(self):
        if hasattr(self, "body"):
            body = getattr(self, "body")
            if hasattr(body, "stream_data") or hasattr(body, "blocks"):
                return extract_text_from_streamfield(body)
            elif isinstance(body, str):
                return strip_tags(body)[:300]
        if hasattr(self, "intro"):
            return strip_tags(getattr(self, "intro"))[:300]
        return ""


def extract_text_from_streamfield(stream_value, max_length=300):
    """
    Recursively extract text from a StreamField value.
    """
    if not stream_value:
        return ""
    text = []
    for block in stream_value:
        value = block.value
        if hasattr(value, "stream_data") or hasattr(
            value, "blocks"
        ):  # Nested StreamBlock
            text.append(extract_text_from_streamfield(value, max_length))
        elif hasattr(value, "source"):  # RichTextBlock
            text.append(str(value.source))
        elif isinstance(value, str):
            text.append(value)
        elif isinstance(value, dict):
            for v in value.values():
                if (
                    hasattr(v, "stream_data")
                    or hasattr(v, "blocks")
                    or isinstance(v, list)
                ):
                    text.append(extract_text_from_streamfield(v, max_length))
                elif isinstance(v, str):
                    text.append(v)
        elif isinstance(value, list):
            text.append(extract_text_from_streamfield(value, max_length))
    combined = strip_tags(" ".join(text))
    return combined[:max_length]
