from django.db import models
from wagtail import blocks
from home.models.custom_blocks.common import link_obj


class IndentStyle(models.TextChoices):
    INDENTED = "indented"
    UNINDENTED = "unindented"


class ListOfLinksBlock(blocks.StructBlock):
    style = blocks.ChoiceBlock(
        choices=[
            ("indented", IndentStyle.INDENTED),
            ("unindented", IndentStyle.UNINDENTED),
        ],
        default=IndentStyle.INDENTED,
        label="List style",
        required=True,
    )

    links = blocks.ListBlock(link_obj.child_block, label="Add Entry")

    class Meta:
        label = "List of Links"
