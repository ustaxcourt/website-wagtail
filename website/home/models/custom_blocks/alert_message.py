from wagtail.blocks import StructBlock, RichTextBlock


class AlertMessageBlock(StructBlock):
    message = RichTextBlock(features=["bold", "italic", "link"])

    class Meta:
        icon = "warning"
        label = "Alert Message"
