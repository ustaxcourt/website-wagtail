from functools import cached_property

from wagtail import blocks
from home.models.custom_blocks.import_export_block import ImportExportBlock
from home.models.custom_blocks.question_answer_block import QuestionAnswerBlock

from home.models.snippets.faq_filter_tag import (
    FAQFilterTag,
)


class QuestionAnswersValue(blocks.StructValue):
    """
    Resolves the FilterTag slugs stored on each question to display names.

    Only relies on each question having a ``filtertag`` slug, so other Q&A blocks
    (e.g. the raw HTML page's) can reuse it with a different question shape.
    """

    @cached_property
    def _tag_names(self):
        slugs = {qa.get("filtertag") for qa in self["questions"]}
        return dict(
            FAQFilterTag.objects.filter(slug__in=slugs).values_list("slug", "name")
        )

    def tag_name(self, slug):
        return self._tag_names.get(slug, "")

    @property
    def filter_tags(self):
        """Distinct (slug, name) pairs in the order they first appear on the questions."""
        seen = {}
        for qa in self["questions"]:
            slug = qa.get("filtertag")
            if slug in self._tag_names and slug not in seen:
                seen[slug] = self._tag_names[slug]
        return list(seen.items())

    @property
    def entries(self):
        """Each question paired with its FilterTag's display name."""
        return [(qa, self.tag_name(qa.get("filtertag"))) for qa in self["questions"]]


class QuestionAnswersBlock(blocks.StructBlock):
    display_filter_section = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Display Filter Section",
        help_text="Show FilterTag buttons above the questions and display each question as an accordion.",
    )

    import_export = ImportExportBlock(
        label="Import/Export Questions",
        help_text="Select .csv file to import",
        file_type_filter=".csv",
    )

    questions = blocks.ListBlock(
        QuestionAnswerBlock(),
        label="Questions",
        help_text="Add a question and answer. Link the anchor tag number. Select the FAQ FilterTag type in the dropdown.",
    )

    class Meta:
        label = "Question and Answer"
        value_class = QuestionAnswersValue
