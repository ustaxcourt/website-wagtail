from wagtail import blocks
from home.models.custom_blocks.common import CommonBlock
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.shortcuts import render
from django.http import Http404
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.search import index

from home.models.snippets.judges import JudgeProfile, JudgeRole
from home.models.custom_blocks.common import custom_promote_panels


judge_snippet = SnippetChooserBlock(
    target_model="home.JudgeCollection",
    required=False,
    help_text="Optionally pick a JudgeCollection snippet",
    label="Judge Collection",
)


class JudgeColumnBlock(CommonBlock):
    judgeCollection = judge_snippet


class JudgeColumns(blocks.StructBlock):
    column = blocks.ListBlock(JudgeColumnBlock())


class JudgeIndex(RoutablePageMixin, Page):
    """
    A specialized page for displaying judges categorized by their titles.
    Only one instance of this page can exist in the site.
    """

    template = "home/enhanced_standard_page.html"
    max_count = 1

    body = StreamField(
        [
            ("columns", JudgeColumns()),
        ],
        blank=True,
        use_json_field=True,
        help_text="Add judge profiles or collections to display on this page",
    )

    content_panels = [
        FieldPanel("title"),
        FieldPanel("body"),
    ]

    promote_panels = custom_promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Get all judge collections
        roles = JudgeRole.objects.filter(
            role_name__in=["Chief Judge", "Chief Special Trial Judge"]
        )
        context["roles"] = roles
        return context

    @route(r"^(?P<id>\d+)/(?P<last_name>[\w-]+)/$")
    def judge_detail(self, request, id, last_name):
        try:
            # Use the ID to find the judge
            judge = JudgeProfile.objects.get(id=id)
            context = self.get_context(request)
            context["judge"] = judge
            if judge.last_name.lower() != last_name:
                raise Http404("Judge not found")
            return render(request, "home/judge_detail.html", context)
        except JudgeProfile.DoesNotExist:
            # Handle case where judge doesn't exist
            raise Http404("Judge not found")

    class Meta:
        verbose_name = "Judges Index Page"
        abstract = False
