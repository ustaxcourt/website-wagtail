from wagtail import blocks

from home.models.config import IconCategories


class IconHeaderBlock(blocks.StructBlock):
    icon = blocks.ChoiceBlock(
        choices=[
            (icon.value, icon.name.replace("_", " ").title()) for icon in IconCategories
        ],
        required=True,
        label="Icon",
    )
    text = blocks.CharBlock(required=True, label="Header Text")

    class Meta:
        label = "Icon Header"
        icon = "title"
