"""
Shared SideCard seed data for the Prepare to File and FAQs pages (WAG-1339
phase 2). Both pages' Figma mockups show the same "Clerk's Office" and "Need
Legal Help?" cards, so the content lives here once instead of being copied
into each page initializer.
"""

import logging
import uuid

from wagtail.documents.models import Document
from wagtail.models import Page

from home.models import SideCard

logger = logging.getLogger(__name__)


def _load_icon(initializer, filename, title):
    doc = Document.objects.filter(title=title).first()
    if doc:
        return doc
    return initializer.load_document_from_documents_dir(
        subdirectory=None, filename=filename, title=title
    )


def add_clerks_office_side_card(initializer, page):
    mail_icon = _load_icon(initializer, "mail.svg", "Mail Icon")
    call_icon = _load_icon(initializer, "call.svg", "Call Icon")

    SideCard.objects.create(
        page=page,
        header_title="Clerk's Office",
        introductory_text="<p>For questions about filing a petition</p>",
        color="blue",
        link_display_style="contact",
        links=[
            {
                "type": "button",
                "value": {
                    "icon": mail_icon.pk,
                    "text": "dawson.support@ustaxcourt.gov",
                    "url": [
                        {
                            "type": "email",
                            "value": "dawson.support@ustaxcourt.gov",
                            "id": str(uuid.uuid4()),
                        }
                    ],
                    "style": "primary",
                },
                "id": str(uuid.uuid4()),
            },
            {
                "type": "button",
                "value": {
                    "icon": call_icon.pk,
                    "text": "(202) 521-0700",
                    "helper_text": "Mon–Fri, 8:00am–4:30pm ET",
                    "url": [
                        {
                            "type": "phone",
                            "value": "(202) 521-0700",
                            "id": str(uuid.uuid4()),
                        }
                    ],
                    "style": "primary",
                },
                "id": str(uuid.uuid4()),
            },
        ],
    )


def add_need_legal_help_side_card(initializer, page):
    open_in_new_icon = _load_icon(initializer, "open_in_new.svg", "Open in New Icon")

    litc_page = Page.objects.filter(slug="clinics-and-pro-bono-programs").first()
    if litc_page:
        litc_url_block = [
            {"type": "internal_page", "value": litc_page.pk, "id": str(uuid.uuid4())}
        ]
    else:
        logger.warning(
            "'clinics-and-pro-bono-programs' page not found - falling back to "
            "the public IRS LITC directory for the 'Need Legal Help?' side card."
        )
        litc_url_block = [
            {
                "type": "external_url",
                "value": "https://www.taxpayeradvocate.irs.gov/litc/",
                "id": str(uuid.uuid4()),
            }
        ]

    SideCard.objects.create(
        page=page,
        header_title="Need Legal Help?",
        introductory_text=(
            "<p>Low Income Taxpayer Clinics (LITCs) provide free or low-cost "
            "representation and tax advice. You may qualify based on income.</p>"
        ),
        color="navy",
        link_display_style="button",
        links=[
            {
                "type": "button",
                "value": {
                    "icon": open_in_new_icon.pk,
                    "icon_location": "after",
                    "text": "Find an LITC Near You",
                    "url": litc_url_block,
                    "style": "inverted-primary",
                },
                "id": str(uuid.uuid4()),
            },
        ],
    )


def add_helpful_links_side_card(initializer, page):
    """
    "Helpful Links" only appears on the FAQs mockup, not Prepare to File.

    The exact target pages weren't specified in the ticket/mockups beyond
    the link labels - guessing at the closest existing pages
    (dawson-user-guides / dawson-faqs-training-and-support) for now; revisit
    once real targets are confirmed.
    """
    user_guides_page = Page.objects.filter(slug="dawson-user-guides").first()
    training_page = Page.objects.filter(slug="dawson-faqs-training-and-support").first()

    links = []
    if user_guides_page:
        links.append(
            {
                "type": "button",
                "value": {
                    "text": "DAWSON Petitioner Electronic Filing Instructions",
                    "url": [
                        {
                            "type": "internal_page",
                            "value": user_guides_page.pk,
                            "id": str(uuid.uuid4()),
                        }
                    ],
                    "style": "primary",
                },
                "id": str(uuid.uuid4()),
            }
        )
    if training_page:
        links.append(
            {
                "type": "button",
                "value": {
                    "text": "DAWSON Petitioner Training Video",
                    "url": [
                        {
                            "type": "internal_page",
                            "value": training_page.pk,
                            "id": str(uuid.uuid4()),
                        }
                    ],
                    "style": "primary",
                },
                "id": str(uuid.uuid4()),
            }
        )

    if not links:
        logger.warning(
            "Neither 'dawson-user-guides' nor "
            "'dawson-faqs-training-and-support' pages were found - skipping "
            "the 'Helpful Links' side card."
        )
        return

    SideCard.objects.create(
        page=page,
        header_title="Helpful Links",
        color="blue",
        link_display_style="plain_links",
        links=links,
    )
