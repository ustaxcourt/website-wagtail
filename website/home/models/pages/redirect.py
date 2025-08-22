from home.models.pages.standard import StandardPage
from home.admin.moderation import ModerationTabbedInterface
from home.models.custom_blocks.common import custom_promote_panels


class RedirectPage(StandardPage):
    content_panels = StandardPage.content_panels

    edit_handler = ModerationTabbedInterface.create_for_page(
        content_panels=content_panels,
        promote_panels=custom_promote_panels,
    )
