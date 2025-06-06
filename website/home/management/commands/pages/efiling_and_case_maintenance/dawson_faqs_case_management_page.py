from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedRawHTMLPage
from home.management.commands.snippets.dawson_faqs_ribbon import (
    dawson_faqs_ribbon_name,
)
import logging

logger = logging.getLogger(__name__)

dawson_faqs_case_management_images = [
    {
        "title": "image of the Dawson faqs case management secured",
        "filename": "dawson_faqs_case_management_secured.jpg",
    },
    {
        "title": "image of the Dawson faqs case management banner",
        "filename": "dawson_faqs_case_management_banner.jpg",
    },
    {
        "title": "image of the Dawson faqs case management document properties",
        "filename": "dawson_faqs_case_management_properties.jpg",
    },
]


class DawsonFaqsCaseManagementPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson-faqs-case-management"
        title = "Frequently Asked Questions About DAWSON"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=dawson_faqs_ribbon_name
        ).first()

        uploaded_images = {}

        for image in dawson_faqs_case_management_images:
            image_uploaded = self.load_image_from_images_dir(
                "dawson", image["filename"], image["title"]
            )

            if image_uploaded:
                uploaded_images[image["filename"]] = {
                    "id": image_uploaded.id,
                    "url": image_uploaded.file.url,
                }

        questions = [
            {
                "question": "Can I file a petition to start a new case in DAWSON?",
                "answer": {
                    "rich_text": """<ul>
                              <li>Yes. Petitions can be filed electronically in DAWSON. For more information, see the <a href="/dawson-user-guides" title="DAWSON User Guides">User Guides</a>.</li>
                              <li>If you file a petition electronically, there is no need to submit an additional paper copy. Likewise, if you have already sent a paper petition to the Court, there is no need to also file a petition electronically.</li>
                              </ul>"""
                },
                "anchortag": "FAQS1",
            },
            {
                "question": "How do I pay the filing fee?",
                "answer": {
                    "rich_text": """During the process of electronically filing your petition, a unique Docket Number will be assigned to your case. You may pay the fee on
                <a href="https://www.pay.gov/public/home" title="Pay.gov">Pay.gov</a>
                 with an accepted payment method (e.g., credit card, bank account (ACH)). Your case Docket Number is required. For more information, see
                 <a href="/pay-filing-fee" title="How to Pay the Filing Fee">How to Pay the Filing Fee</a>."""
                },
                "anchortag": "FAQS2",
            },
            {
                "question": "Do I need to submit courtesy copies for eFiled documents over 50 pages?",
                "answer": {
                    "rich_text": """No. The requirement for mailed courtesy copies of eFiled documents longer than 50 pages is suspended until further notice."""
                },
                "anchortag": "FAQS3",
            },
            {
                "question": "How are consolidated cases handled in DAWSON?",
                "answer": {
                    "rich_text": """<ul>
                                <li>Parties to consolidated cases have the ability to electronically file documents simultaneously in all of the consolidated cases.</li>
                                <li>Entries of Appearance for <strong>petitioner representatives</strong> and Decisions must still be filed in each case separately.</li>
                                <li>Refer to the <a href="/release-notes" title="DAWSON Release Notes">DAWSON Release Notes</a> for more information, or the <a href="/dawson-user-guides" title="DAWSON User Guides">User Guides</a>.
                                  for detailed instructions on how to electronically file documents in consolidated cases.</li>
                                 </ul>"""
                },
                "anchortag": "FAQS4",
            },
            {
                "question": "How are sealed cases and sealed documents handled in DAWSON?",
                "answer": {
                    "rich_text": """<ul>
                                  <li>Sealed Cases
                                      <ul>
                                         <li>Parties wishing to file a Petition under seal must file the Petition on paper along with a Motion to Seal. The Motion should specify whether it seeks to seal the entire case or only the Petition.</li>
                                         <li>Parties wishing to seal a case that is already docketed must file a Motion to Seal.</li>
                                         <li>With the exception of an initial pleading or entry of appearance, parties may file documents in a sealed case in the same manner as filing documents in a case that is not sealed (including eFiling in DAWSON).</li>
                                      </ul>
                                  </li>
                                  <li>Sealed Documents
                                      <ul>
                                      <li>Specific documents on the docket record can be sealed in two ways.
                                          <ul>
                                              <li>A document may be sealed from the public.</li>
                                              <li>A document may be sealed from the public and from the parties to the case.</li>
                                          </ul>
                                      </li>
                                      <li>Parties wishing to file a new document under seal must file the document in paper along with a Motion to Seal specifying whether it is to be sealed from the public or the public and the parties.</li>
                                      <li>Parties wishing to seal a document that has previously been filed (e.g., after discovering missed redactions) may electronically file a Motion to Seal specifying whether it is to be sealed from the public or the public and the parties.</li>
                                    </ul>
                                  </li>
                                    <li>For more information, see the <a href="/dawson-user-guides" title="DAWSON User Guides">User Guides</a>.</li>
                              </ul>"""
                },
                "anchortag": "FAQS5",
            },
            {
                "question": "Why did I receive an error when I uploaded a file in DAWSON?",
                "answer": {
                    "html_block": """<ol>
                                         <li>
                                             <strong>Error Message: File size too big</strong>
                                             <ul>
                                                 <li>If your document is larger than 250MB, you should upload the information in separate documents. Each document must be 250MB or less.</li>
                                             </ul>
                                         </li>
                                         <li>
                                            <strong>Error Message: The file is corrupt or in an unsupported PDF format</strong>
                                             <ul>
                                                 <li>
                                                     There are a few options:
                                                     <ul>
                                                         <li>Resave the file, ensuring that it opens without error in Adobe.</li>
                                                         <li>When saving the file, select "Print to PDF".</li>
                                                         <li>Print the document and use a scanner to create and save a new PDF document.</li>
                                                     </ul>
                                                 </li>
                                             </ul>
                                         </li>
                                         <li>
                                             <strong>Error Message: Your firewall or network may be preventing submission.</strong>
                                             <ul>
                                                 <li>Try submitting again while on a different network/Wi-Fi. If you have success on a different network, you may need to have your network administrator adjust your network's firewall settings to allow document submissions to <a href="https://dawson.ustaxcourt.gov" data-original-title="" title="">https://dawson.ustaxcourt.gov</a>.</li>
                                             </ul>
                                         </li>
                                         <li>
                                             <strong>Error Message: There is a problem with this file</strong>
                                             <ul>
                                                 <li>Your internet browser may be outdated. Please update your browser to the current version and try the upload again.</li>
                                             </ul>
                                         </li>
                                         <li>
                                             <strong>Error Message: The file is encrypted or password protected</strong>
                                             <ul>
                                                 <li>If you signed your document electronically with an application like Adobe, it may have asked you to save the document as a read-only copy that cannot be modified. If you saved your document as a read-only copy, it may have been password protected by Adobe automatically (unbeknownst to you).</li>
                                                 <li>To troubleshoot, review your document(s).
                                                     <ul>
                                                         <li>When viewing your document(s), are you seeing a blue banner and "(SECURED)" at the top of the document?</li>
                                                     </ul>
                                                 </li>
                                             </ul>
                                         </li>
                                     </ol>
                                     <p style="text-align: center">
                                     <img src="{secured_image_url}" alt="image of the Dawson faqs case management secured" class="fullwidth" />
                                     </p>
                                      <ul>
                                         <li>
                                             <strong>YES</strong> - Do ONE of the following steps below to create a new unsecured document file for your submission:
                                                 <ol>
                                                     <li>Create a new document file, and when signing it, decline Adobe's prompt to save a read-only copy by clicking "Cancel" on the screen when prompted. This will prevent Adobe from automatically applying security measures to the file.</li>
                                                 </ol>
                                         </li>
                                     </ul>
                                     <p style="text-align: center">
                                         <img src="{banner_image_url}" alt="image of the Dawson faqs case management banner" class="fullwidth" />
                                      </p>
                                         <ul style="margin-left: 1.5rem; list-style-type: none;">
                                            <li>2. Print the document and scan it back in as a new document file. The new file will not have the security measures applied.</li>
                                         </ul>
                                     <ul>
                                         <li >
                                         <strong>NO</strong> - If you do NOT see the above banner or "(SECURED)" in the document window, follow these steps.
                                         </li>
                                     </ul>

                                     <ol style="margin-left: 2.5rem;">
                                         <li>Right-click in the document.</li>
                                         <li>Choose Document Properties from the options.</li>
                                         <li>Click on the Security tab.</li>
                                         <li>In the dropdown menu labeled Security Method, select "No Security".</li>
                                         <li>Click OK</li>
                                     </ol>
                                     <p style="text-align: center">
                                     <img src="{document_properties_image_url}" alt="image of the Dawson faqs case management document properties" class="fullwidth" />
                                     </p>

                                     <ul style="margin-left: 1.5rem; list-style-type: none;">
                                         <li>6. Save the document. You should now be able to upload the document to DAWSON without error.</li>
                                     </ul>""".format(
                        secured_image_url=uploaded_images[
                            "dawson_faqs_case_management_secured.jpg"
                        ]["url"],
                        banner_image_url=uploaded_images[
                            "dawson_faqs_case_management_banner.jpg"
                        ]["url"],
                        document_properties_image_url=uploaded_images[
                            "dawson_faqs_case_management_properties.jpg"
                        ]["url"],
                    ),
                },
                "anchortag": "FAQS6",
            },
            {
                "question": "What digital signatures are accepted in DAWSON?",
                "answer": {
                    "rich_text": """
                        <ul>
                            <li>
                                Acceptable digital signatures in DAWSON:
                                <ul>
                                    <li>Parties may submit a high-resolution or PDF document bearing either imaged or digitized signatures in satisfaction of the requirements of Rule 23(a)(3), Tax Court Rules of Practice and Procedure.</li>
                                    <li>PDFs of documents bearing an actual signature are acceptable. (Print and sign before turning into a PDF.)</li>
                                    <li>Documents signed using an authentication program (e.g., Adobe or DocuSign) are acceptable. Be sure to remove encryption or password protection prior to uploading into DAWSON.</li>
                                    <li>Stylized signatures (e.g., signing with "/" or using cursive font) are only acceptable when paired with the DAWSON username (email address) and password or with authorization. See Rule 23(a)(3).</li>
                                    <li>Stylized signatures on paper submitted forms are not acceptable.</li>
                                </ul>
                            </li>

                            <li>
                                Documents that require a signature in addition to that of the eFiler, e.g., both spouses are petitioners:
                                <ul>
                                    <li>Documents uploaded to DAWSON should be signed by the additional party, using the guidance above, before being uploaded.</li>
                                    <li>If you chose to auto-generate a Petition in DAWSON and your spouse has authorized you to file an electronic petition, then the signature block on the petition auto-generated by DAWSON will serve as your spouse's signature.</li>
                                </ul>
                            </li>
                        </ul>
                         """
                },
                "anchortag": "FAQS7",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedRawHTMLPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="DAWSON: Case Management",
                body=[
                    {"type": "h2", "value": "DAWSON: Case Management"},
                ],
                raw_html_body=[
                    {"type": "questionanswers", "value": questions},
                ],
                show_in_menus=False,
            )
        )

        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")
