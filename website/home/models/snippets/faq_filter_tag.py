import json
import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, PublishingPanel
from wagtail.models import (
    DraftStateMixin,
    RevisionMixin,
    WorkflowMixin,
    get_page_models,
)
from wagtail.fields import StreamField
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, UnpublishView

from home.admin.moderation import ModerationTabbedInterface
from home.forms import ReviewByRequiredOnSubmitSnippetForm
from home.mixins.moderation import ModerationMixin

logger = logging.getLogger(__name__)

QA_BLOCK_TYPE = "questionanswers"
RESERVED_TAG_NAMES = {"all"}


class FAQFilterTag(
    ModerationMixin, WorkflowMixin, DraftStateMixin, RevisionMixin, models.Model
):
    """
    A FilterTag option that can be applied to a Question and Answer.

    Q&As store the tag's ``slug`` rather than its name. The slug is generated once
    and never changes, so renaming a tag updates every Q&A that uses it.
    """

    name = models.CharField(
        max_length=100,
        help_text="Name of the FilterTag as shown in the Q&A dropdown. Must be unique (not case-sensitive).",
    )
    slug = models.SlugField(max_length=120, unique=True, editable=False)
    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="faqfiltertag"
    )

    content_panels = [FieldPanel("name")]
    panels = content_panels + [PublishingPanel()]
    edit_handler = ModerationTabbedInterface.create_for_snippet(content_panels)

    class Meta:
        verbose_name = "FAQ FilterTag"
        verbose_name_plural = "FAQ FilterTags"
        ordering = [Lower("name")]
        constraints = [
            models.UniqueConstraint(
                Lower("name"), name="unique_faq_filter_tag_name_ci"
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def revisions(self):
        return self._revisions

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()
        if self.name.casefold() in RESERVED_TAG_NAMES:
            raise ValidationError(
                {
                    "name": '"All" cannot be used as a FilterTag option. '
                    "The FAQs page provides an All button automatically."
                }
            )
        if self.expire_at:
            # A scheduled expiry would unpublish the tag without the in-use check
            raise ValidationError(
                {"expire_at": "FilterTags cannot be scheduled to expire."}
            )
        if (
            FAQFilterTag.objects.filter(name__iexact=self.name)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                {
                    "name": f'A FilterTag option with the value "{self.name}" already exists.'
                }
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_slug()
        super().save(*args, **kwargs)

    def _generate_slug(self):
        base = slugify(self.name) or "tag"
        slug, suffix = base, 2
        while FAQFilterTag.objects.filter(slug=slug).exists():
            slug = f"{base}-{suffix}"
            suffix += 1
        return slug


def get_faq_filter_tag_choices():
    """Live FilterTags as (slug, name) choices, alphabetical and case-insensitive."""
    return [(tag.slug, tag.name) for tag in FAQFilterTag.objects.filter(live=True)]


def _find_qas_with_tag(node, slug):
    """Yield the Q&A dicts tagged with ``slug`` anywhere in raw StreamField data."""
    if isinstance(node, dict):
        if node.get("type") == QA_BLOCK_TYPE:
            items = node.get("value") or []
            for item in items:
                # ListBlock items are {"type": "item", "value": {...}} or bare dicts
                qa = item.get("value", item) if isinstance(item, dict) else None
                if isinstance(qa, dict) and qa.get("filtertag") == slug:
                    yield qa
        for value in node.values():
            yield from _find_qas_with_tag(value, slug)
    elif isinstance(node, list):
        for value in node:
            yield from _find_qas_with_tag(value, slug)


def get_filter_tag_usage(tag):
    """
    Return the Q&As using ``tag`` as a list of ``(page, question)`` tuples.

    Both the saved page content and the latest draft revision are checked, so a Q&A
    that only exists in an unpublished draft still blocks removal.
    """
    usage = []
    seen = set()
    for model in get_page_models():
        stream_fields = [
            f.name for f in model._meta.get_fields() if isinstance(f, StreamField)
        ]
        if not stream_fields:
            continue
        for page in model.objects.select_related("latest_revision"):
            sources = [list(getattr(page, name).raw_data) for name in stream_fields]
            revision = page.latest_revision
            if revision is not None:
                for name in stream_fields:
                    content = revision.content.get(name)
                    sources.append(
                        json.loads(content) if isinstance(content, str) else content
                    )
            for source in sources:
                for qa in _find_qas_with_tag(source, tag.slug):
                    key = (page.pk, qa.get("anchortag"), qa.get("question"))
                    if key not in seen:
                        seen.add(key)
                        usage.append((page, qa.get("question") or "(no question text)"))
    return usage


def block_if_filter_tags_in_use(request, tags, action):
    """
    Refuse ``action`` ("removed" or "unpublished") for FilterTags that a Q&A still uses.

    Returns a redirect to the FilterTag list with an error naming the Q&As, or None
    when every tag is free to go.
    """
    blocked = False
    for tag in tags:
        if not isinstance(tag, FAQFilterTag):
            continue
        usage = get_filter_tag_usage(tag)
        if not usage:
            continue
        blocked = True
        logger.info(f'FilterTag "{tag.name}" is in use by {len(usage)} Q&A(s).')
        messages.error(
            request,
            format_html(
                'The FilterTag "{}" cannot be {} because it is used by the '
                "following Q&As. Reassign them to another tag or delete them first:{}",
                tag.name,
                action,
                format_html_join(
                    "",
                    '<br>&bull; "{}" on <a href="{}">{}</a>',
                    (
                        (
                            question,
                            reverse("wagtailadmin_pages:edit", args=[page.pk]),
                            page.title,
                        )
                        for page, question in usage
                    ),
                ),
            ),
        )
    if blocked:
        return redirect(reverse("wagtailsnippets_home_faqfiltertag:list"))


class FAQFilterTagUnpublishView(UnpublishView):
    """
    Refuse up front when the tag is in use, instead of showing a confirm page whose
    "referenced N times" count can't see tags stored as slugs inside Q&As.
    """

    def get(self, request, *args, **kwargs):
        response = block_if_filter_tags_in_use(request, [self.object], "unpublished")
        return response or super().get(request, *args, **kwargs)


class FAQFilterTagViewSet(SnippetViewSet):
    model = FAQFilterTag
    form_class = ReviewByRequiredOnSubmitSnippetForm
    icon = "tag"
    unpublish_view_class = FAQFilterTagUnpublishView
    list_display = ["name", "slug"]


register_snippet(FAQFilterTagViewSet)
