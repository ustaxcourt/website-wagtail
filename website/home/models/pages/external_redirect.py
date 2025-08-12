from wagtail.models import Page
from home.mixins.moderation import ModerationMixin
from home.admin.moderation import ModerationTabbedInterface
from home.models.custom_blocks.common import custom_promote_panels


class ExternalRedirectPage(ModerationMixin, Page):
    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=Page.content_panels, promote_panels=custom_promote_panels
    )

    class Meta:
        abstract = False
