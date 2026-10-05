from wagtail import blocks
from home.models.snippets.faq_filter_tag import (
    get_faq_filter_tag_choices,
)


class QuestionAnswerBlock(blocks.StructBlock):
    question = blocks.CharBlock(required=False)
    answer = blocks.RichTextBlock()
    anchortag = blocks.CharBlock()
    filtertag = blocks.ChoiceBlock(
        choices=get_faq_filter_tag_choices,
        required=True,
        label="FilterTag",
    )
