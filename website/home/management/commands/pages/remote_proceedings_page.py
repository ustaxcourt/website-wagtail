from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import RemoteProceedingsPage
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationCategories
from home.models import RemoteProceedingsFAQLinks
from home.models import RemoteProceedingsInfo
from home.models import RemoteProceedingsExample


class RemoteProceedingsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "zoomgov"
        title = "Remote Proceedings"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        # Load the PDF document
        # document = self.load_document_from_documents_dir(
        #     "citation_style_manual",
        #     "USTC_Citation_and_Style_Manual_modified_2024.09.pdf",
        #     "USTC Citation and Style Manual",
        # )

        # if not document:
        #     return

        content_type = ContentType.objects.get_for_model(RemoteProceedingsPage)

        new_page = home_page.add_child(
            instance=RemoteProceedingsPage(
                title=title,
                body=(
                    "This guide provides resources about the Court's Zoomgov remote proceedings."
                ),
                slug=slug,
                seo_title=title,
                search_description="Resources about the Court's Zoomgov remote proceedings",
                content_type=content_type,
                show_in_menus=True,
                feedback_form="Recently had a Zoomgov proceeding before the Tax Court? Please share your thoughts on the experience by completing the <a href='https://forms.office.com/Pages/ResponsePage.aspx?id=ffQzvB8vfUKKwjrrqKsOvbIIXUQtrfJAgSED0uDb9B9UQzNKSDNIRVFCS1hIRzVVVzg4QkZEUUZTSC4u'>Zoomgov Proceeding Feedback</a> form.",
                faq_title="Zoomgov Remote Proceedings FAQs",
                additional_info="Remote Proceeding Information",
                example_title="Examples of Zoomgov Remote Proceedings",
                example_body="These videos are merely examples. Any resemblance to actual persons, living or dead, or actual events, is purely coincidental.",
            )
        )

        RemoteProceedingsPage.objects.filter(id=new_page.id).update(
            menu_item_name="REMOTE PROCEEDINGS",
            navigation_category=NavigationCategories.RULES_AND_GUIDANCE,
        )

        links = [
            {
                "title": "The Basics",
                "link": "https://ustaxcourt.gov/zoomgov_the_basics.html",
            },
            {
                "title": "Getting Ready",
                "link": "https://ustaxcourt.gov/zoomgov_getting_ready.html",
            },
            {
                "title": "Zoomgov Proceedings",
                "link": "https://ustaxcourt.gov/zoomgov_zoomgov_proceedings.html",
            },
        ]

        for link in links:
            entry = RemoteProceedingsFAQLinks(
                link=link["link"],
                title=link["title"],
                parentpage=new_page,
            )
            entry.save()

        info = [
            {
                "title": "Sample Notice Setting Case For Trial for Remote Proceedings",
                "document": "subpoenas_for_remote_proceedings.pdf",
            },
            {
                "title": "Sample Standing Pretrial Order for Remote Proceedings",
                "document": "sample_standing_pretrial_order.pdf",
            },
            {
                "title": "Sample Pretrial Memorandum for Remote Proceedings",
                "document": "sample_pretrial_memorandum.pdf",
            },
            {
                "title": "Sample Standing Pretrial Order for Small Tax Cases for Remote Proceedings",
                "document": "sample_standing_pretrial_order_small_tax_cases.pdf",
            },
            {
                "title": "Frequently Asked Questions About Remote Proceedings",
                "document": "zoomgov_faqs.pdf",
            },
            {
                "title": "Guidance Regarding Documentary Evidence for Remote Proceedings",
                "document": "documentary_evidence.pdf",
            },
            {
                "title": " Guidance Regarding Subpoenas for Remote Proceedings",
                "document": "subpoenas_for_remote_proceedings.pdf",
            },
        ]

        for info in info:
            document = self.load_document_from_documents_dir(
                "remote_proceedings",
                info["document"],
                info["title"],
            )

            entry = RemoteProceedingsInfo(
                pdf=document,
                parentpage=new_page,
            )
            entry.save()

        examples = [
            {
                "title": "Pre-Calendar Call: Trial Clerk Recognizes Participants",
                "speaker_title": "Pre-Calendar Call (Speaker View)",
                "speaker_url": "https://www.zoomgov.com/rec/play/7pJ-JuCurzg3HNaR5gSDAv4rW429Lq-s0Hcb8_YKy0myUiFRY1LwNbYQMefqMqaX-dQY9AnaOUhUsr2z",
                "gallery_title": "Pre-Calendar Call (Gallery View)",
                "gallery_url": "https://www.zoomgov.com/rec/play/ucIkJeCoqTg3E9bH5QSDUaJxW9W8Lvms1yIX-KEOy0vgV3lWMVWhNLZHMOQBvv_6k5lqDN-gJndD3J78",
            },
            {
                "title": "Clinic Breakout Room: Clinics Arrange Assistance for a Self-represented Taxpayer",
                "speaker_title": "Clinic Breakout Room (Speaker View)",
                "speaker_url": "https://www.zoomgov.com/rec/play/6ccoceD6_W03GoWX5gSDAfV9W465fKusg3BP__pfnRq0VCEDO1avNLESYOAbTabklbv0yiWi66n5kSov",
                "gallery_title": "Clinic Breakout Room (Gallery View)",
                "gallery_url": "https://www.zoomgov.com/rec/play/vJZ4cLyhqTM3E9yW4wSDCvEsW43sLams0XNMr_RZnUfnV3NWOwWuMrYQNOGlcdk8kfHJoxKiMQj7Tpnh",
            },
            {
                "title": "Calendar Call: Judge Calls the Calendar and Schedules Trials",
                "speaker_title": "Calendar Call (Speaker View)",
                "speaker_url": "https://www.zoomgov.com/rec/play/7MZ_Ib39-Gg3GtHG4QSDB_IrW9W9LqOs0iBIrPcJmEixBXQHO1aibrYRYeb8-AOwY7azVe501K-jLlNW",
                "gallery_title": "Calendar Call (Gallery View)",
                "gallery_url": "https://www.zoomgov.com/rec/play/6cd-Juz9rW83SdyV5gSDB6UoW469K_is0yVM8vIMnh3hVXFXNgKvbrdANOuhsffnej1FlzyLFf5yXorg",
            },
            {
                "title": "Trial: Judge Conducts a Trial",
                "speaker_title": "Trial (Speaker View)",
                "speaker_url": "https://www.zoomgov.com/rec/play/vJ15Iu37rDI3SNWRsASDVqQsW9W4f6qshykW_6ENmUy8BXgDNVT3Y-cUNOtJy1Csd5uM_q_l1h92qJyk",
                "gallery_title": "Trial (Gallery View)",
                "gallery_url": "https://www.zoomgov.com/rec/play/vZV_c-us-DM3E9zGuQSDU6UtW466fK-s1SJPr6AMyUrmWiYBZ1unZ-RAJhhPJ3q-2_gTftw65Yr0Lg",
            },
        ]

        for example in examples:
            entry = RemoteProceedingsExample(
                title=example["title"],
                speaker_title=example["speaker_title"],
                speaker_url=example["speaker_url"],
                gallery_title=example["gallery_title"],
                gallery_url=example["gallery_url"],
                parentpage=new_page,
            )
            entry.save()

        self.logger.write(f"Successfully created the '{title}' page.")
