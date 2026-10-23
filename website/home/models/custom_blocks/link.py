from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from home.models.config import IconCategories


class LinkBlock(blocks.StructBlock):
    def __init__(self, **kwargs):
        local_blocks = [
            ("title", blocks.CharBlock()),
            (
                "icon",
                blocks.ChoiceBlock(
                    choices=[
                        (
                            icon.value,
                            icon.name.replace("_", " ").title(),
                        )
                        for icon in IconCategories
                    ],
                    required=False,
                ),
            ),
            (
                "document",
                DocumentChooserBlock(required=False),
            ),
            (
                "video",
                DocumentChooserBlock(required=False),
            ),
            ("url", blocks.CharBlock(required=False)),
            (
                "text_only",
                blocks.BooleanBlock(required=False),
            ),
        ]

        # Pass local_blocks to StructBlock's init
        super().__init__(local_blocks=local_blocks, **kwargs)

    # title = blocks.CharBlock()
    # icon = blocks.ChoiceBlock(
    #     choices=[
    #         (
    #             icon.value,
    #             icon.name.replace("_", " ").title(),
    #         )
    #         for icon in IconCategories
    #     ],
    #     required=False,
    # ),
    # document = DocumentChooserBlock(required=False),
    # video = DocumentChooserBlock(required=False),
    # url = blocks.CharBlock(required=False)
    # text_only = blocks.BooleanBlock(required=False),

    def clean(self, value):
        result = super().clean(value)

        properties = [
            value.bound_blocks["document"].value,
            value.bound_blocks["video"].value,
            value.bound_blocks["url"].value,
            value.bound_blocks["text_only"].value,
        ]
        properties_with_value = sum(1 for p in properties if p)
        if properties_with_value != 1:
            from django.core.exceptions import ValidationError

            raise ValidationError(
                "Exactly one of Document, Video, Url, or Text Only must be provided."
            )

        return result

    class Meta:
        label = "Item"
