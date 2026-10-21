from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import PetitionerExperiencePage
from urllib.parse import urljoin
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

docs = {
    "DAWSON_Public_Training_Guide.pdf": "",
    "DAWSON_Petitioner_Training_Guide.pdf": "",
    "DAWSON_Practitioner_Training_Guide.pdf": "",
    "petitioners-how-to-efile-a-petition-in-dawson.mp4": "",
    "efiling_in_consolidated_cases.mp4": "",
}

icons = {
    "PDF_icon.svg": "",
    "videocam-icon.svg": "",
    "computer_icon.svg": "",
    "search_icon.svg": "",
}


class DawsonUserGuidesPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson-user-guides"
        title = "DAWSON User Guides & Electronic Filing Instructions"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        for doc_name in docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            docs[doc_name] = document

        for icon_name in icons.keys():
            icon = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=icon_name,
                title=icon_name,
            )
            icons[icon_name] = icon

        _base_url = getattr(settings, "BASE_URL", "")

        _dawson_how_to_e_file_a_petition = urljoin(
            _base_url, "/dawson-how-to-e-file-a-petition"
        )
        _dawson_how_to_merge_pdfs = urljoin(_base_url, "/dawson-how-to-merge-pdfs")
        _dawson_troubleshoot_file_uploads = urljoin(
            _base_url, "/dawson-troubleshoot-file-uploads"
        )
        _dawson_how_to_search_for_a_case = urljoin(
            _base_url, "/dawson-how-to-search-for-a-case"
        )
        _dawson_how_to_search_for_an_order = urljoin(
            _base_url, "/dawson-how-to-search-for-an-order"
        )
        _dawson_how_to_search_for_an_opinion = urljoin(
            _base_url, "/dawson-how-to-search-for-an-opinion"
        )
        _dawson_how_to_update_contact_info = urljoin(
            _base_url, "/dawson-how-to-update-contact-info"
        )
        _dawson_how_to_view_dashboard = urljoin(
            _base_url, "/dawson-how-to-view-dashboard"
        )

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        new_page = home_page.add_child(
            instance=PetitionerExperiencePage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
                introductory_text="Explore guides and videos designed to help you navigate and use DAWSON, the United States Tax Court's electronic filing and case management system. These resources provide step-by-step guidance for filing documents, managing your case, and using key DAWSON features.",
                show_floating_definitions_button=True,
                body=[
                    {
                        "type": "quick_access_tiles",
                        "value": {
                            "tiles_hover_enabled": True,
                            "icon_position": "desktop_top_mobile_left",
                            "tiles": [
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "DAWSON Self-Represented (Pro se) Electronic Filing Instructions",
                                        "description": '<p data-block-key="hy3pw">How to e-file a petition in DAWSON</p>',
                                        "icon": {
                                            "svg_file": icons["PDF_icon.svg"].pk,
                                        },
                                        "content_alignment": "center",
                                        "link": [
                                            {
                                                "type": "external_url",
                                                "value": urljoin(
                                                    _base_url,
                                                    docs[
                                                        "DAWSON_Petitioner_Training_Guide.pdf"
                                                    ].url,
                                                ),
                                                "id": "9393518a-620b-48d0-ad76-f7b31541e438",
                                            }
                                        ],
                                    },
                                    "id": "e88caaf3-2aef-4522-8516-bd30b1ecaf5b",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "DAWSON Public Training Guide",
                                        "description": '<p data-block-key="61gx3">How to navigate DAWSON key features</p>',
                                        "icon": {
                                            "svg_file": icons["PDF_icon.svg"].pk,
                                        },
                                        "content_alignment": "center",
                                        "link": [
                                            {
                                                "type": "external_url",
                                                "value": urljoin(
                                                    _base_url,
                                                    docs[
                                                        "DAWSON_Public_Training_Guide.pdf"
                                                    ].url,
                                                ),
                                                "id": "691e4ed5-c4d9-4223-807b-e6bd7153478c",
                                            }
                                        ],
                                    },
                                    "id": "7240874e-f6d6-4c2b-a283-5671fb42e90e",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "DAWSON Practitioner Electronic Filing Instructions",
                                        "description": '<p data-block-key="61gx3">How to e-file a petition in DAWSON</p>',
                                        "icon": {
                                            "svg_file": icons["PDF_icon.svg"].pk,
                                        },
                                        "content_alignment": "center",
                                        "link": [
                                            {
                                                "type": "external_url",
                                                "value": urljoin(
                                                    _base_url,
                                                    docs[
                                                        "DAWSON_Practitioner_Training_Guide.pdf"
                                                    ].url,
                                                ),
                                                "id": "6435a064-efb1-47e2-882d-3b731532fe2d",
                                            }
                                        ],
                                    },
                                    "id": "cb21d215-26c8-4f1a-9254-e836a60bc9cc",
                                },
                            ],
                        },
                        "id": "0aeaa220-b215-4bc1-a55a-452a017df016",
                    },
                    {
                        "type": "quick_access_tiles",
                        "value": {
                            "tiles_hover_enabled": True,
                            "icon_position": "desktop_top_mobile_left",
                            "tiles": [
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "DAWSON Training Video: Petitioners",
                                        "description": '<p data-block-key="t7059">How to e-file a petition in DAWSON</p>',
                                        "icon": {
                                            "svg_file": icons["videocam-icon.svg"].pk,
                                        },
                                        "content_alignment": "center",
                                        "link": [
                                            {
                                                "type": "external_url",
                                                "value": urljoin(
                                                    _base_url,
                                                    docs[
                                                        "petitioners-how-to-efile-a-petition-in-dawson.mp4"
                                                    ].url,
                                                ),
                                                "id": "dc97676e-1cde-4123-bf81-49df407fcb24",
                                            }
                                        ],
                                    },
                                    "id": "1e7919de-1033-4540-8494-3aea993ce3ad",
                                },
                                {
                                    "type": "item",
                                    "value": {
                                        "title": "DAWSON Training Video: Parties",
                                        "description": '<p data-block-key="61gx3">How to simultaneously e-file documents in consolidated cases</p>',
                                        "icon": {
                                            "svg_file": icons["videocam-icon.svg"].pk,
                                        },
                                        "content_alignment": "center",
                                        "link": [
                                            {
                                                "type": "external_url",
                                                "value": urljoin(
                                                    _base_url,
                                                    docs[
                                                        "efiling_in_consolidated_cases.mp4"
                                                    ].url,
                                                ),
                                                "id": "1d0ea423-1d50-47ff-8ab1-7e4128f328f6",
                                            }
                                        ],
                                    },
                                    "id": "5703204c-1b08-4efd-8d41-cb9e563a9482",
                                },
                            ],
                        },
                        "id": "c9d4064c-2277-4d20-b0f4-9c7843281762",
                    },
                    {
                        "type": "paragraph",
                        "value": '<h2 data-block-key="cnklq"><b>DAWSON Topic-Specific Guides</b></h2><p data-block-key="582ej">These detailed topic guides provide step-by-step instructions for completing common actions in DAWSON, the Court\'s electronic filing and case management system. Select a guide below to learn about specific topics, such as filing and managing cases, searching Court records, updating account information, and using other DAWSON features.</p>',
                        "id": "d6e5e2bc-4a70-43a2-842a-96b2689d6bc1",
                    },
                    {
                        "type": "section_header",
                        "value": {
                            "heading": "Starting a Case",
                            "style": "blue_bar",
                            "link_text": "",
                            "link_url": "",
                        },
                        "id": "99db1622-d317-4a9f-bbd0-0d9976f74b67",
                    },
                    {
                        "type": "card",
                        "value": [
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": icons["computer_icon.svg"].pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "Starting a case",
                                    "title": "How to e-file a petition",
                                    "description": '<p data-block-key="5j6a9">Read this guide before filing to prepare and submit your petition in DAWSON.</p>',
                                    "buttons": [
                                        {
                                            "type": "item",
                                            "value": {
                                                "icon": None,
                                                "icon_location": "before",
                                                "text": "View Guide",
                                                "url": [
                                                    {
                                                        "type": "external_url",
                                                        "value": _dawson_how_to_e_file_a_petition,
                                                        "id": "29f6a183-4b39-443a-ae15-85973007ca82",
                                                    }
                                                ],
                                                "style": "primary",
                                                "button_hover": True,
                                                "helper_text": "",
                                                "download": False,
                                            },
                                            "id": "689a126d-f0b9-4006-b724-8cbbcba5d536",
                                        }
                                    ],
                                },
                                "id": "315e5b7a-bc7a-4325-90d6-8d0ae5f8bb11",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": icons["PDF_icon.svg"].pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "Starting a case",
                                    "title": "How to merge PDFs",
                                    "description": '<p data-block-key="k9szf">Read this guide to combine multiple PDF files into a single document.</p>',
                                    "buttons": [
                                        {
                                            "type": "item",
                                            "value": {
                                                "icon": None,
                                                "icon_location": "before",
                                                "text": "View Guide",
                                                "url": [
                                                    {
                                                        "type": "external_url",
                                                        "value": _dawson_how_to_merge_pdfs,
                                                        "id": "e71589ea-ea1c-4e01-9f91-e382a3cb6095",
                                                    }
                                                ],
                                                "style": "primary",
                                                "button_hover": True,
                                                "helper_text": "",
                                                "download": False,
                                            },
                                            "id": "7bca8805-9c66-4688-a3c8-4ed06e5d4266",
                                        }
                                    ],
                                },
                                "id": "2a072c34-60e7-42ba-8f8b-b542767a1e7c",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": icons["PDF_icon.svg"].pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "Starting a case",
                                    "title": "How to troubleshoot file upload errors",
                                    "description": '<p data-block-key="k9szf">Read this guide to troubleshoot common file upload errors</p>',
                                    "buttons": [
                                        {
                                            "type": "item",
                                            "value": {
                                                "icon": None,
                                                "icon_location": "before",
                                                "text": "View Guide",
                                                "url": [
                                                    {
                                                        "type": "external_url",
                                                        "value": _dawson_troubleshoot_file_uploads,
                                                        "id": "62e6fb63-7b5a-47b5-bf58-b2be0b5b6411",
                                                    }
                                                ],
                                                "style": "primary",
                                                "button_hover": True,
                                                "helper_text": "",
                                                "download": False,
                                            },
                                            "id": "9c7ead20-3cb6-4341-8b88-75e03fe71cb9",
                                        }
                                    ],
                                },
                                "id": "00052936-5f51-41f6-ad98-7a5cba04d2b5",
                            },
                        ],
                        "id": "9d5fc1a5-3a4a-472c-a533-fee906eac374",
                    },
                    {
                        "type": "section_header",
                        "value": {
                            "heading": "Search DAWSON",
                            "style": "blue_bar",
                            "link_text": "",
                            "link_url": "",
                        },
                        "id": "427c5b18-dd71-4822-b1c8-a52f0b283314",
                    },
                    {
                        "type": "card",
                        "value": [
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": icons["search_icon.svg"].pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "Search DAWSON",
                                    "title": "How to search for a case",
                                    "description": '<p data-block-key="5j6a9">Read this guide to find a case using a docket number or petitioner name.</p>',
                                    "buttons": [
                                        {
                                            "type": "item",
                                            "value": {
                                                "icon": None,
                                                "icon_location": "before",
                                                "text": "View Guide",
                                                "url": [
                                                    {
                                                        "type": "external_url",
                                                        "value": _dawson_how_to_search_for_a_case,
                                                        "id": "c73137e1-2918-4378-856c-0fef34e67a3a",
                                                    }
                                                ],
                                                "style": "primary",
                                                "button_hover": True,
                                                "helper_text": "",
                                                "download": False,
                                            },
                                            "id": "edf3ef45-5f54-4064-bd1d-15dc5db0ff8c",
                                        }
                                    ],
                                },
                                "id": "315e5b7a-bc7a-4325-90d6-8d0ae5f8bb11",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": icons["search_icon.svg"].pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "Search DAWSON",
                                    "title": "How to search for an order",
                                    "description": '<p data-block-key="k9szf">Read this guide to find court orders using DAWSON search tools.</p>',
                                    "buttons": [
                                        {
                                            "type": "item",
                                            "value": {
                                                "icon": None,
                                                "icon_location": "before",
                                                "text": "View Guide",
                                                "url": [
                                                    {
                                                        "type": "external_url",
                                                        "value": _dawson_how_to_search_for_an_order,
                                                        "id": "93c54c91-fd05-4e98-8d81-80cdb5fe2b34",
                                                    }
                                                ],
                                                "style": "primary",
                                                "button_hover": True,
                                                "helper_text": "",
                                                "download": False,
                                            },
                                            "id": "dbf6a910-49c3-4dc8-8f3a-136cf7cae46f",
                                        }
                                    ],
                                },
                                "id": "7bbe2243-7ed0-472b-8fa6-e99b37270d57",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": icons["search_icon.svg"].pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "Search DAWSON",
                                    "title": "How to search for an opinion",
                                    "description": '<p data-block-key="k9szf">Read this guide to find court opinions using DAWSON search tools.</p>',
                                    "buttons": [
                                        {
                                            "type": "item",
                                            "value": {
                                                "icon": None,
                                                "icon_location": "before",
                                                "text": "View Guide",
                                                "url": [
                                                    {
                                                        "type": "external_url",
                                                        "value": _dawson_how_to_search_for_an_opinion,
                                                        "id": "f2f3cef5-1d09-43b6-bbc0-0feae0e844ea",
                                                    }
                                                ],
                                                "style": "primary",
                                                "button_hover": True,
                                                "helper_text": "",
                                                "download": False,
                                            },
                                            "id": "5f375c9f-f634-4448-92e5-6d61a488e04e",
                                        }
                                    ],
                                },
                                "id": "38317847-8481-4130-8a19-978fd3c90e37",
                            },
                        ],
                        "id": "21d95900-e908-4cdf-b233-a4469b527dd7",
                    },
                    {
                        "type": "section_header",
                        "value": {
                            "heading": "DAWSON Account Management",
                            "style": "blue_bar",
                            "link_text": "",
                            "link_url": "",
                        },
                        "id": "7c8a1c99-ac6c-483f-ac38-0dfa8ae9f2a9",
                    },
                    {
                        "type": "card",
                        "value": [
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": icons["computer_icon.svg"].pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "DAWSON Account Management",
                                    "title": "How to update contact information",
                                    "description": '<p data-block-key="8erb6">Read this guide to update your contact information in DAWSON.</p>',
                                    "buttons": [
                                        {
                                            "type": "item",
                                            "value": {
                                                "icon": None,
                                                "icon_location": "before",
                                                "text": "View Guide",
                                                "url": [
                                                    {
                                                        "type": "external_url",
                                                        "value": _dawson_how_to_update_contact_info,
                                                        "id": "362e30a8-4ab8-40dd-8972-0aa9fbaeee6a",
                                                    }
                                                ],
                                                "style": "primary",
                                                "button_hover": True,
                                                "helper_text": "",
                                                "download": False,
                                            },
                                            "id": "35565d23-bbf5-4cc0-9197-ff2108ba4f28",
                                        }
                                    ],
                                },
                                "id": "92a1121d-ff38-4faf-b903-0b9226a994a6",
                            },
                            {
                                "type": "item",
                                "value": {
                                    "color": "white",
                                    "numbered_icon": "",
                                    "numbered_icon_alignment": "left",
                                    "title_icon": icons["computer_icon.svg"].pk,
                                    "title_icon_alt_text": "",
                                    "subtitle": "DAWSON Account Management",
                                    "title": "How to view the DAWSON dashboard",
                                    "description": '<p data-block-key="77zje">Read this guide to navigate your DAWSON dashboard and view your cases.</p>',
                                    "buttons": [
                                        {
                                            "type": "item",
                                            "value": {
                                                "icon": None,
                                                "icon_location": "before",
                                                "text": "View Guide",
                                                "url": [
                                                    {
                                                        "type": "external_url",
                                                        "value": _dawson_how_to_view_dashboard,
                                                        "id": "0a6de403-4957-45f9-b93e-75de14bda2b4",
                                                    }
                                                ],
                                                "style": "primary",
                                                "button_hover": True,
                                                "helper_text": "",
                                                "download": False,
                                            },
                                            "id": "397062d7-9299-488d-8ea8-dfd62c7455f7",
                                        }
                                    ],
                                },
                                "id": "544ed410-2807-4f81-8e64-a37fb8da1da2",
                            },
                        ],
                        "id": "f956fb29-1ba7-40e2-89ee-937c6c172d7a",
                    },
                ],
            ),
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")
