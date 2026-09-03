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
    level = blocks.ChoiceBlock(
        choices=[
            ("h2", "Heading 2"),
            ("h3", "Heading 3"),
            ("h4", "Heading 4"),
            ("h5", "Heading 5"),
        ],
        required=True,
        label="Heading Level",
        default="h2",
    )

    class Meta:
        label = "Icon Header"
        icon = "title"
