from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.shortcuts import render
from django.http import Http404
from wagtail.search import index
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface

from home.models.snippets.judges import (
    JudgeProfile,
    JudgeRole,
    JudgeCollection,
    PrivateSeminarDisclosure,
    RESTRICTED_ROLES,
)
from home.models.custom_blocks.common import custom_promote_panels
from home.blocks import QuickAccessTilesBlock

# Keep these exported for backward compatibility with __init__.py imports
# (they are no longer used by JudgeIndex itself)
from wagtail import blocks
from home.models.custom_blocks.common import CommonBlock
from wagtail.snippets.blocks import SnippetChooserBlock

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


TYPE_ORDER = [
    "Judge",
    "Senior Judge",
    "Special Trial Judge",
    "Senior Special Trial Judge",
]

FILTER_KEYS = {
    "Judge": "judges",
    "Senior Judge": "senior-judges",
    "Special Trial Judge": "special-trial-judges",
    "Senior Special Trial Judge": "senior-special-trial-judges",
}

FILTER_LABELS = {
    "Judge": "Judges",
    "Senior Judge": "Senior Judges",
    "Special Trial Judge": "Special Trial Judges",
    "Senior Special Trial Judge": "Senior Special Trial Judges",
}

SECTION_LABELS_SINGULAR = {
    "Judge": "Judge Biography",
    "Senior Judge": "Senior Judge Biography",
    "Special Trial Judge": "Special Trial Judge Biography",
    "Senior Special Trial Judge": "Senior Special Trial Judge Biography",
}

SECTION_LABELS_PLURAL = {
    "Judge": "Judge Biographies",
    "Senior Judge": "Senior Judge Biographies",
    "Special Trial Judge": "Special Trial Judge Biographies",
    "Senior Special Trial Judge": "Senior Special Trial Judge Biographies",
}


class JudgeIndex(ModerationMixin, RoutablePageMixin, Page):
    """
    A specialized page for displaying judges categorized by their titles.
    Only one instance of this page can exist in the site.
    """

    template = "home/judge_information.html"
    max_count = 1

    intro_text = RichTextField(
        blank=True,
        default="See the Judge's biography by clicking on the cards.",
        help_text="Introductory text displayed below the page title.",
    )

    bottom_tiles = StreamField(
        [("quick_access_tiles", QuickAccessTilesBlock())],
        blank=True,
        use_json_field=True,
        help_text="Quick-access tiles rendered below the judge card grid.",
    )

    content_panels = [
        FieldPanel("title"),
        FieldPanel("intro_text"),
        FieldPanel("bottom_tiles"),
    ]

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels, promote_panels=custom_promote_panels
    )

    promote_panels = custom_promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
    ]

    def _build_judge_groups(self):
        """Build ordered judge groups from JudgeCollection objects."""
        # Pre-fetch all role assignments for quick lookup
        roles_by_judge_id = {}
        for role in JudgeRole.objects.select_related("judge").all():
            if role.judge_id:
                roles_by_judge_id[role.judge_id] = role.role_name

        groups = []
        for judge_type in TYPE_ORDER:
            collection_name = judge_type + "s"
            try:
                collection = JudgeCollection.objects.get(name=collection_name)
            except JudgeCollection.DoesNotExist:
                continue

            ordered_judges = list(
                collection.ordered_judges.select_related("judge").all()
            )
            if not ordered_judges:
                continue

            judges_with_roles = []
            for orderable in ordered_judges:
                judge = orderable.judge
                role_label = roles_by_judge_id.get(judge.id, judge.title)
                judges_with_roles.append(
                    {
                        "judge": judge,
                        "role_label": role_label,
                    }
                )

            # Sort: restricted roles (Chief Judge / Chief Special Trial Judge) first,
            # then all others alphabetically by last name then first name.
            judges_with_roles.sort(
                key=lambda d: (
                    0 if d["role_label"] in RESTRICTED_ROLES else 1,
                    d["judge"].last_name.lower(),
                    d["judge"].first_name.lower(),
                )
            )

            count = len(judges_with_roles)
            label = (
                SECTION_LABELS_SINGULAR[judge_type]
                if count == 1
                else SECTION_LABELS_PLURAL[judge_type]
            )

            groups.append(
                {
                    "type": judge_type,
                    "label": label,
                    "filter_label": FILTER_LABELS[judge_type],
                    "judges": judges_with_roles,
                    "filter_key": FILTER_KEYS[judge_type],
                }
            )

        return groups

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        judge_groups = self._build_judge_groups()
        context["judge_groups"] = judge_groups

        # URL for the judicial conduct page
        judicial_conduct_page = Page.objects.filter(
            slug="judicial-conduct-and-disability-procedures"
        ).first()
        context["judicial_conduct_url"] = (
            judicial_conduct_page.url if judicial_conduct_page else "#"
        )

        return context

    @route(r"^(?P<id>\d+)/(?P<last_name>[\w-]+)/$")
    def judge_detail(self, request, id, last_name):
        try:
            judge = JudgeProfile.objects.get(id=id)
            context = self.get_context(request)
            context["judge"] = judge
            if judge.last_name.lower() != last_name:
                raise Http404("Judge not found")
            return render(request, "home/judge_detail.html", context)
        except JudgeProfile.DoesNotExist:
            raise Http404("Judge not found")

    @route(r"^private-seminar-disclosures/$")
    def private_seminar_disclosures(self, request):
        context = self.get_context(request)
        all_disclosures = PrivateSeminarDisclosure.objects.select_related(
            "judge"
        ).order_by("-date", "judge__last_name")

        years = sorted(
            all_disclosures.dates("date", "year", order="DESC"),
            reverse=True,
        )
        selected_year = request.GET.get("year", "")
        if selected_year:
            try:
                all_disclosures = all_disclosures.filter(date__year=int(selected_year))
            except (ValueError, TypeError):
                selected_year = ""

        context["disclosures"] = all_disclosures
        context["years"] = [y.year for y in years]
        context["selected_year"] = selected_year
        return render(request, "home/private_seminar_disclosures.html", context)

    class Meta:
        verbose_name = "Judges Index Page"
        abstract = False
