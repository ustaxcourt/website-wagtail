from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage
from home.management.commands.snippets.dawson_faqs_ribbon import (
    dawson_faqs_ribbon_name,
)


class DawsonFaqsCaseManagementPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "dawson_faqs_case_management"
        title = "Frequently Asked Questions About DAWSON"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name=dawson_faqs_ribbon_name
        ).first()

        questions = [
            {
                "question": "Can I file a petition to start a new case in DAWSON?",
                "answer": """<ul>
                              <li>Yes. Petitions can be filed electronically in DAWSON. For more information, see the <strong><a href="/dawson_user_guides" target="_blank" title="DAWSON User Guides">User Guides</a></strong>.</li>
                              <li>If you file a petition electronically, there is no need to submit an additional paper copy. Likewise, if you have already sent a paper petition to the Court, there is no need to also file a petition electronically.</li>
                              </ul>""",
                "anchortag": "FAQS1",
            },
            {
                "question": "How do I pay the filing fee?",
                "answer": """During the process of electronically filing your petition, a unique Docket Number will be assigned to your case. You may pay the fee on
                <strong><a href="https://www.pay.gov/public/home" title="Pay.gov">Pay.gov</a></strong>
                 with an accepted payment method (e.g., credit card, bank account (ACH)). Your case Docket Number is required. For more information, see
                 <strong><a href="https://www.ustaxcourt.gov/pay_filing_fee.html" title="How to Pay the Filing Fee">How to Pay the Filing Fee</a></strong>.""",
                "anchortag": "FAQS2",
            },
            {
                "question": "Do I need to submit courtesy copies for eFiled documents over 50 pages?",
                "answer": """No. The requirement for mailed courtesy copies of eFiled documents longer than 50 pages is suspended until further notice.""",
                "anchortag": "FAQS3",
            },
            {
                "question": "How are consolidated cases handled in DAWSON?",
                "answer": """<ul>
                                <li>Parties to consolidated cases have the ability to electronically file documents simultaneously in all of the consolidated cases.</li>
                                <li>Entries of Appearance for <strong>petitioner representatives</strong> and Decisions must still be filed in each case separately.</li>
                                <li>Refer to the <strong><a href="https://www.ustaxcourt.gov/release_notes.html" title="DAWSON Release Notes">DAWSON Release Notes</a></strong> for more information, or the <strong><a href="/dawson_user_guides" target="_blank" title="DAWSON User Guides">User Guides</a></strong>.
                                  for detailed instructions on how to electronically file documents in consolidated cases.</li>
                                 </ul>""",
                "anchortag": "FAQS4",
            },
            {
                "question": "How are sealed cases and sealed documents handled in DAWSON?",
                "answer": """<ul>
                                  <li>Sealed Cases</li>
                                      <ul>
                                         <li>Parties wishing to file a Petition under seal must file the Petition on paper along with a Motion to Seal. The Motion should specify whether it seeks to seal the entire case or only the Petition.</li>
                                         <li>Parties wishing to seal a case that is already docketed must file a Motion to Seal.</li>
                                         <li>With the exception of an initial pleading or entry of appearance, parties may file documents in a sealed case in the same manner as filing documents in a case that is not sealed (including eFiling in DAWSON).</li>
                                      </ul>
                                  <li>Sealed Documents</li>
                                      <ul>
                                      <li>Specific documents on the docket record can be sealed in two ways.</li>
                                          <ul>
                                          <li>A document may be sealed from the public.</li>
                                          <li>A document may be sealed from the public and from the parties to the case.</li>
                                          </ul>
                                      <li>Parties wishing to file a new document under seal must file the document in paper along with a Motion to Seal specifying whether it is to be sealed from the public or the public and the parties.</li>
                                      <li>Parties wishing to seal a document that has previously been filed (e.g., after discovering missed redactions) may electronically file a Motion to Seal specifying whether it is to be sealed from the public or the public and the parties.</li>
                                      </ul>
                                     <li>For more information, see the <strong><a href="/dawson_user_guides" target="_blank" title="DAWSON User Guides">User Guides</a></strong>.</li>
                              </ul>""",
                "anchortag": "FAQS5",
            },
            {
                "question": "Why did I receive an error when I uploaded a file in DAWSON?",
                "answer": """<ol>
                             <li><strong>Error Message: File size too big</strong>

                             <ul>
                             <li>If your document is larger than 250MB, you should upload the information in separate documents. Each document must be 250MB or less.</li>
                             </ul></li>
                             <li><strong>Error Message: The file is corrupt or in an unsupported PDF format</strong>

                             <ul>
                             <li>There are a few options:

                             <ul>
                             <li>Resave the file, ensuring that it opens without error in Adobe.</li>
                             <li>When saving the file, select “Print to PDF”.</li>
                             <li>Print the document and use a scanner to create and save a new PDF document.</li>
                             </ul></li>
                             </ul></li>
                             <li><strong>Error Message: Your firewall or network may be preventing submission</strong>.

                             <ul>
                             <li>Try submitting again while on a different network/Wi-Fi. If you have success on a different network, you may need to have your network administrator adjust your network’s firewall settings to allow document submissions to <a href="https://dawson.ustaxcourt.gov" data-original-title="" title="">https://dawson.ustaxcourt.gov</a>.</li>
                             </ul></li>
                             <li><strong>Error Message: There is a problem with this file</strong>

                             <ul>
                             <li>Your internet browser may be outdated. Please update your browser to the current version and try the upload again.</li>
                             </ul></li>
                             <li><strong>Error Message: The file is encrypted or password protected</strong>

                             <ul>
                             <li>If you signed your document electronically with an application like Adobe, it may have asked you to save the document as a read-only copy that cannot be modified. If you saved your document as a read-only copy, it may have been password protected by Adobe automatically (unbeknownst to you). </li>
                             <li>To troubleshoot, review your document(s).

                             <ul>
                             <li>When viewing your document(s), are you seeing a blue banner and "(SECURED)" at the top of the document?</li>
                             </ul></li>
                             </ul></li>
                             </ol>""",
                "anchortag": "FAQS7",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="DAWSON: Case Management",
                body=[
                    {"type": "h2", "value": "DAWSON: Case Management"},
                    {"type": "questionanswers", "value": questions},
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
