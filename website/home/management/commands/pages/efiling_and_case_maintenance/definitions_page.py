from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)
docs = ["Rule-21_Amended_03202023.pdf", "Rule-245.pdf"]
slug = "definitions"
title = "Definitions"


class DawsonFaqsDefinitionsPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists)")
            return
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        """generate the definitions page"""

        definition_docs = {
            doc: self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc,
                title=doc,
            )
            for doc in docs
        }

        page_body = (
            '<p>“Designated Service Person” means the'
            " practitioner designated to receive service of documents in a case. The"
            " first counsel of record is generally the Designated Service Person, see"
            ' <a linktype="document"'
            f' id="{definition_docs["Rule-21_Amended_03202023.pdf"].id}"><b>Rule'
            " 21(b)(2)</b></a>. The ability to designate an additional service person"
            ' in DAWSON is coming soon.</p><p>“Document”'
            " means any written matter filed by or with the Court including, but not"
            " limited to motions, pleadings, applications, petitions, notices,"
            " declarations, affidavits, exhibits, briefs, memoranda of law, orders,"
            ' and deposition transcripts.</p><p>“eLodged”'
            " refers to any document that is electronically submitted to the Court"
            " with a motion for leave through DAWSON and that is not automatically"
            ' filed.</p><p>“Intervenor” is a third party'
            " who has an interest in the outcome of the case. The most common example"
            " is the spouse or former spouse of a petitioner seeking innocent spouse"
            " relief. “Participant” is a partner who elects to participate in a"
            " partnership action by filing a notice of election to participate under"
            f' <a linktype="document" id="{definition_docs["Rule-245.pdf"].id}"><b>Rule'
            ' 245</b></a>.</p><p>“Party”, for purposes of'
            " electronic access, means either petitioner(s) or respondent"
            ' (IRS).</p><p>“PDF” means Portable Document'
            " Format. Documents in PDF may be opened in Adobe Reader or an equivalent"
            " viewer. Adobe Reader may be downloaded free of charge from the Adobe"
            " website (www.adobe.com). Electronic documents may be converted to PDF"
            " through a word processor, third party PDF creation software such as"
            " Adobe Acrobat, or online PDF creation services from Adobe (<a"
            ' href="https://createpdf.adobe.com/">https://createpdf.adobe.com/</a>) and'
            " others. Documents in paper form may be scanned into PDF.</p>"
            '<p>“Pro Se” means a petitioner who represents'
            " themselves without a lawyer or an entity appearing through an authorized"
            ' fiduciary or officer.</p><p>For additional'
            ' terms, please visit the <a href="/petitioners-glossary" title="Guidance for Petitioners: Glossary">glossary</a>.</p>'
        )

        content_type = ContentType.objects.get_for_model(EnhancedStandardPage)
        home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                body=[
                    {
                        "type": "paragraph",
                        "value": page_body,
                    }
                ],
                slug=slug,
                seo_title=title,
                search_description=title,
                content_type=content_type,
            )
        )
        logger.info(f"Successfully created the '{title}' page.")
