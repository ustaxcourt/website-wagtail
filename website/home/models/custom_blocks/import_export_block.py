from functools import cached_property

from django import forms
from wagtail import blocks
from django.utils.translation import gettext_lazy as _
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.telepath import register
# from home.models.custom_blocks.question_answer_block import QuestionAnswerBlock


class ImportExportBlock(blocks.StructBlock):
    def __init__(self, local_blocks=None, file_type_filter="", **kwargs):
        super().__init__(local_blocks, **kwargs)
        self.accept = file_type_filter

    # questions = blocks.ListBlock(
    #     QuestionAnswerBlock(),
    #     label="Questions",
    #     help_text="Add a question and answer. Link the anchor tag number. Select the FAQ FilterTag type in the dropdown.",
    # )

    class Meta:
        form_template = "import_export_block_form.html"

    def get_form_context(self, value, prefix="", errors=None):
        context = super().get_form_context(value, prefix, errors)
        context["instructions"] = _(
            "Use 'Choose File' or drag/drop to import data from file."
        )
        context["accept"] = self.accept
        return context


class ImportExportBlockAdapter(StructBlockAdapter):
    js_constructor = "blocks.models.ImportExportBlock"

    @cached_property
    def media(self):
        structblock_media = super().media
        return forms.Media(
            js=structblock_media._js + ["home/js/import_export_block.js"],
            css={"all": ("home/css/import_export_block.css",)},
        )


register(ImportExportBlockAdapter(), ImportExportBlock)
