from django.db import models
from wagtail import blocks
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from home.models.config import IconCategories

from wagtail.blocks import PageChooserBlock
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.models import DraftStateMixin, LockableMixin, RevisionMixin
from wagtail.models import PreviewableMixin
from wagtail.fields import StreamField
from django.core.exceptions import ValidationError


class NavigationRibbonLink(models.Model):
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=200, choices=IconCategories.choices)
    url = models.CharField(max_length=1000)

    navigation_ribbon = ParentalKey(
        "NavigationRibbon", related_name="links", on_delete=models.CASCADE
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("icon"),
        FieldPanel("url"),
    ]


@register_snippet
class NavigationRibbon(ClusterableModel):
    name = models.CharField(max_length=255)

    panels = [
        InlinePanel("links", label="Links"),  # Now properly references the ParentalKey
    ]

    def __str__(self):
        return self.name


class SubNavigationLinkBlock(blocks.StructBlock):
    """Represents a sub-navigation link that can point to internal or external pages"""

    title = blocks.CharBlock(
        required=True, help_text="Display text for the navigation link"
    )
    page = PageChooserBlock(required=False, help_text="Select a page to link to")
    external_url = blocks.URLBlock(required=False, help_text="Or enter an external URL")

    class Meta:
        icon = "link"


@register_snippet
class NavigationMenu(
    PreviewableMixin, DraftStateMixin, LockableMixin, RevisionMixin, ClusterableModel
):
    def clean(self):
        super().clean()
        # Check if another menu already exists during creation
        if not self.pk and NavigationMenu.objects.exists():
            raise ValidationError("Only one Navigation Menu can exist in the system.")

    menu_items = StreamField(
        [
            (
                "section",
                blocks.StructBlock(
                    [
                        (
                            "title",
                            blocks.CharBlock(
                                required=True, help_text="Top level navigation title"
                            ),
                        ),
                        (
                            "external_url",
                            blocks.URLBlock(
                                required=False, help_text="Or enter an external URL"
                            ),
                        ),
                        ("sub_links", blocks.ListBlock(SubNavigationLinkBlock())),
                    ]
                ),
            )
        ],
        use_json_field=True,
        blank=True,
    )

    def get_preview_template(self, request, mode_name):
        return "previews/header_preview.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context["self"] = self
        return context

    # Required for RevisionMixin
    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="navigation_menu"
    )

    panels = [
        FieldPanel("menu_items"),
    ]

    @property
    def revisions(self):
        return self._revisions

    class Meta:
        verbose_name = "Navigation Menu"
        verbose_name_plural = "Navigation Menus"

    def __str__(self):
        return "Navigation Menu"

    @classmethod
    def get_active_menu(cls):
        return cls.objects.filter(live=True).first()
