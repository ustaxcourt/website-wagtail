import datetime

from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from django.db import models
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

    seminar_intro_text = RichTextField(
        blank=True,
        default=(
            "The following are private seminar disclosures submitted by judges "
            "of the United States Tax Court."
        ),
        help_text="Introductory text shown at the top of the Private Seminar Disclosures page.",
    )

    seminar_empty_text = models.CharField(
        max_length=500,
        blank=True,
        default="There are no disclosures to report at this time.",
        help_text=(
            "Text displayed on the Private Seminar Disclosures page when there "
            "are no current disclosures within the configured time window."
        ),
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
        FieldPanel("seminar_intro_text"),
        FieldPanel("seminar_empty_text"),
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
            # Preserve only valid judge-type filters when returning to the
            # Judge Information page from a biography.
            raw_filters = request.GET.get("filters", "")
            valid_filters = set(FILTER_KEYS.values())
            selected_filters = [
                token
                for token in raw_filters.split(",")
                if token and token in valid_filters
            ]
            context["back_url"] = self.url
            if selected_filters:
                context["back_url"] = f"{self.url}?filters={','.join(selected_filters)}"
            if judge.last_name.lower() != last_name:
                raise Http404("Judge not found")
            return render(request, "home/judge_detail.html", context)
        except JudgeProfile.DoesNotExist:
            raise Http404("Judge not found")

    @route(r"^private-seminar-disclosures/$")
    def private_seminar_disclosures(self, request):
        from home.models.settings import PrivateSeminarDisclosureSettings
        from django.core.paginator import Paginator

        # Determine the disclosure window from the configurable setting.
        settings_obj = PrivateSeminarDisclosureSettings.load(request_or_site=request)
        disclosure_years = settings_obj.disclosure_years

        today = datetime.date.today()
        try:
            cutoff = today.replace(year=today.year - disclosure_years)
        except ValueError:
            # Handles 29 Feb when the cutoff year is not a leap year.
            cutoff = today.replace(year=today.year - disclosure_years, day=28)

        base_qs = (
            PrivateSeminarDisclosure.objects.select_related("judge")
            .filter(date__gte=cutoff)
            .order_by("-date", "judge__last_name")
        )

        # Build the year dropdown from the filtered window only.
        available_years = sorted(
            {d.date.year for d in base_qs},
            reverse=True,
        )

        selected_year = request.GET.get("year", "").strip()

        # Redirect bare ?year= (empty string) to the clean URL so "All Years"
        # removes the query param entirely rather than leaving ?year=.
        if "year" in request.GET and selected_year == "":
            from django.shortcuts import redirect as django_redirect

            return django_redirect(request.path)

        disclosures = base_qs
        if selected_year:
            try:
                disclosures = base_qs.filter(date__year=int(selected_year))
            except (ValueError, TypeError):
                selected_year = ""

        # Paginate — 10 cards per page (Figma shows numbered pagination)
        paginator = Paginator(disclosures, 10)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context = self.get_context(request)
        context["disclosures"] = page_obj
        context["page_obj"] = page_obj
        context["paginator"] = paginator
        context["years"] = available_years
        context["selected_year"] = selected_year
        context["disclosure_years"] = disclosure_years
        return render(request, "home/private_seminar_disclosures.html", context)

    class Meta:
        verbose_name = "Judges Index Page"
        abstract = False
