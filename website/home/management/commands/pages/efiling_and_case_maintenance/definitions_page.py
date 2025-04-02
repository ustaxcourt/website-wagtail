from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import StandardPage
import logging


logger = logging.getLogger(__name__)
docs = ["Rule-21_Amended_03202023.pdf", "Rule-245.pdf"]
slug = "definitions"
title = "Definitions"


class DawsonFaqsDefinitionsPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        if Page.objects.filter(slug=slug).exists():
            # logger.warning(f"- {title} page already exists)")
            self.logger.write(f"- {title} page already exists)")
            return
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        """generate the definitions page"""

        definition_docs = {
            doc: self.load_document_from_documents_dir(None, doc, doc) for doc in docs
        }

        page_body = (
            '<p data-block-key="gxnu3">“Designated Service Person” means the'
            " practitioner designated to receive service of documents in a case. The"
            " first counsel of record is generally the Designated Service Person, see"
            ' <a linktype="document"'
            f' id="{definition_docs["Rule-21_Amended_03202023.pdf"].id}"><b>Rule'
            " 21(b)(2)</b></a>. The ability to designate an additional service person"
            ' in DAWSON is coming soon.<br/></p><p data-block-key="hctv">“Document”'
            " means any written matter filed by or with the Court including, but not"
            " limited to motions, pleadings, applications, petitions, notices,"
            " declarations, affidavits, exhibits, briefs, memoranda of law, orders,"
            ' and deposition transcripts.<br/></p><p data-block-key="b8ojv">“eLodged”'
            " refers to any document that is electronically submitted to the Court"
            " with a motion for leave through DAWSON and that is not automatically"
            ' filed.<br/></p><p data-block-key="408m7">“Intervenor” is a third party'
            " who has an interest in the outcome of the case. The most common example"
            " is the spouse or former spouse of a petitioner seeking innocent spouse"
            " relief. “Participant” is a partner who elects to participate in a"
            " partnership action by filing a notice of election to participate under"
            f' <a linktype="document" id="{definition_docs["Rule-245.pdf"].id}"><b>Rule'
            ' 245</b></a>.<br/></p><p data-block-key="9sv9q">“Party”, for purposes of'
            " electronic access, means either petitioner(s) or respondent"
            ' (IRS).<br/></p><p data-block-key="5i9et">“PDF” means Portable Document'
            " Format. Documents in PDF may be opened in Adobe Reader or an equivalent"
            " viewer. Adobe Reader may be downloaded free of charge from the Adobe"
            " website (www.adobe.com). Electronic documents may be converted to PDF"
            " through a word processor, third party PDF creation software such as"
            " Adobe Acrobat, or online PDF creation services from Adobe (<a"
            ' href="http://createpdf.adobe.com/)">http://createpdf.adobe.com/)</a> and'
            " others. Documents in paper form may be scanned into PDF.<br/></p><p"
            ' data-block-key="8bdcg">“Pro Se” means a petitioner who represents'
            " themselves without a lawyer or an entity appearing through an authorized"
            ' fiduciary or officer.<br/></p><p data-block-key="8h41i">For additional'
            ' terms, please visit the <a linktype="page"'
            ' id="26"><b>glossary</b></a>.</p>'
        )

        content_type = ContentType.objects.get_for_model(StandardPage)
        home_page.add_child(
            instance=StandardPage(
                title=title,
                body=page_body,
                slug=slug,
                seo_title=title,
                search_description=title,
                content_type=content_type,
            )
        )
        # logger.info(f"Successfully created the '{title}' page.")
        self.logger.write(f"Successfully created the '{title}' page.")
