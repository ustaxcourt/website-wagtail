from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import DefinitionsPage
import logging

logger = logging.getLogger(__name__)


class DefinitionsPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()
        self.slug = "definitions"

    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.info("Root page (home) does not exist.")
            return

        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        title = "Definitions"

        if Page.objects.filter(slug=self.slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        # Load required documents
        definition_docs = {
            "rule-21.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="rule-21.pdf",
                title="rule-21.pdf",
            ),
            "rule-245.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="rule-245.pdf",
                title="rule-245.pdf",
            ),
            "rule-37.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="rule-37.pdf",
                title="rule-37.pdf",
            ),
            "rule-151.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="rule-151.pdf",
                title="rule-151.pdf",
            ),
            "rule-173.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="rule-173.pdf",
                title="rule-173.pdf",
            ),
            "rule-280.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="rule-280.pdf",
                title="rule-280.pdf",
            ),
            "rule-350.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="rule-350.pdf",
                title="rule-350.pdf",
            ),
            "Form_4_Statement_of_Taxpayer_Identification_Number.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="Form_4_Statement_of_Taxpayer_Identification_Number.pdf",
                title="Form_4_Statement_of_Taxpayer_Identification_Number.pdf",
            ),
            "Form_5_Request_for_Place_of_Trial.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="Form_5_Request_for_Place_of_Trial.pdf",
                title="Form_5_Request_for_Place_of_Trial.pdf",
            ),
            "Petition_Kit.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="Petition_Kit.pdf",
                title="Petition_Kit.pdf",
            ),
            "Pretrial_Memorandum_Form_old.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="Pretrial_Memorandum_Form_old.pdf",
                title="Pretrial_Memorandum_Form_old.pdf",
            ),
            "Subpoena_Appear_Testify_Hearing_Or_Trial.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="Subpoena_Appear_Testify_Hearing_Or_Trial.pdf",
                title="Subpoena_Appear_Testify_Hearing_Or_Trial.pdf",
            ),
            "Subpoena_To_Testify_Deposition.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="Subpoena_To_Testify_Deposition.pdf",
                title="Subpoena_To_Testify_Deposition.pdf",
            ),
            "tou.pdf": self.load_document_from_documents_dir(
                subdirectory=None,
                filename="tou.pdf",
                title="tou.pdf",
            ),
        }

        # All definitions combined from original Definitions page and Glossary page
        all_definitions = [
            {
                "question": "Abatement",
                "answer": f'<p>Abatement cases ask the IRS to lessen the amount of interest owed when certain requirements are met. See I.R.C. section 6404 and <strong><a linktype="document" id="{definition_docs["rule-280.pdf"].id}" target="_blank" title="Tax Court Rule 280">Tax Court Rule 280</a></strong> et seq. regarding Actions for Review of Failure to Abate Interest.</p>',
            },
            {
                "question": "Answer",
                "answer": "<p>The document respondent files in response to a petition, admitting or denying each allegation in the petition.</p>",
            },
            {
                "question": "Appeals Court",
                "answer": "<p>Generally, regular cases may be appealed (by either party) to the United States Court of Appeals for the circuit in which the petitioner lived when the petition was filed.</p>",
            },
            {
                "question": "Appeals Office",
                "answer": "<p>References to the Appeals Office are usually to the IRS Independent Office of Appeals. Similarly, an Appeals Officer works in that office.</p>",
            },
            {
                "question": "At issue",
                "answer": f'<p>A case is deemed "at issue" once the petition and answer have been filed. In some very limited circumstances where a reply is required, the case will be at issue after a reply to the answer is filed. See <strong><a linktype="document" id="{definition_docs["rule-37.pdf"].id}" target="_blank" title="Rules 37">Rules 37</a></strong> or <strong><a linktype="document" id="{definition_docs["rule-173.pdf"].id}" target="_blank" title="173">173</a></strong>.</p>',
            },
            {
                "question": "Audit",
                "answer": "<p>Although there are different types of audits, an audit is an examination of one's tax returns for a given year or series of years by the IRS.</p>",
            },
            {
                "question": "Bench Opinion",
                "answer": "<p>An oral opinion rendered by the Judge at the close of trial.</p>",
            },
            {
                "question": "Brief",
                "answer": f'<p>A brief is a formal document normally filed by each party after the trial in a regular case. A brief contains a table of contents, a statement of the issues, proposed findings of facts, points of law relied upon, argument and analysis. See <strong><a linktype="document" id="{definition_docs["rule-151.pdf"].id}" target="_blank" title="Rule 151">Rule 151</a></strong>.</p>',
            },
            {
                "question": "Burden of Proof",
                "answer": "<p>The taxpayer who is asking the Court to change the IRS's determination must present evidence to the Court which will support his/her position, and must persuade the Judge that the evidence supports the taxpayer's position.</p>",
            },
            {
                "question": "Calendar Call",
                "answer": "<p>Calendar call occurs on the first day of a trial session (normally Monday) and provides the Judge with the opportunity to ensure that all cases listed on the docket are ready for trial or other disposition. All parties are required to attend unless specifically excused.</p>",
            },
            {
                "question": "Caption",
                "answer": "<p>The caption refers to the name of the parties (e.g., Dan & Susan Smith, Petitioners v. Commissioner of Internal Revenue, Respondent).</p>",
            },
            {
                "question": "CDP",
                "answer": "<p>Collection Due Process (CDP) refers to cases in which the collection of taxes is being made by IRS lien or levy under I.R.C. sections 6320 and/or 6330. A CDP case has a docket number ending in <b>L</b>, for example, 77899-14L.</p>",
            },
            {
                "question": "Certificate of Service",
                "answer": "<p>A <strong>Certificate of Service</strong> is used to show that you have sent or delivered documents to another party, typically the opposing counsel.</p>",
            },
            {
                "question": "Collection Review Case",
                "answer": "<p>See CDP.</p>",
            },
            {
                "question": "DAWSON",
                "answer": "<p>The Court's case management system. <a href='/dawson'>Find out more</a>.</p>",
            },
            {
                "question": "Decision",
                "answer": "<p>A decision document closes a case. A decision is signed by a Judge and entered in the Court's record. The decision reflects the conclusions of the Court. A decision can be entered in a case after the parties have settled all issues or the Judge has issued an opinion or order deciding all issues in a case.</p>",
            },
            {
                "question": "Designated Service Person",
                "answer": f'<p>"Designated Service Person" means the practitioner designated to receive service of documents in a case. The first counsel of record is generally the Designated Service Person, see <a linktype="document" id="{definition_docs["rule-21.pdf"].id}"><b>Rule 21(b)(2)</b></a>. The ability to designate an additional service person in DAWSON is coming soon.</p>',
            },
            {
                "question": "Discovery",
                "answer": '<p>The parties can seek to obtain information and documents necessary to present their case. "Interrogatories" are written questions asked of the opposing party and a "request for documents" is a request to obtain documents and records. Before making a formal request for interrogatories or documents, the parties should talk with one another and make an informal request.</p>',
            },
            {
                "question": "Docket Number",
                "answer": "<p>A multi-digit number the Court assigns to each case for tracking purposes. The last two digits represent the year in which the petition was filed. Small Tax Case docket numbers always end in S.</p>",
            },
            {
                "question": "Document",
                "answer": '<p>"Document" means any written matter filed by or with the Court including, but not limited to motions, pleadings, applications, petitions, notices, declarations, affidavits, exhibits, briefs, memoranda of law, orders, and deposition transcripts.</p>',
            },
            {
                "question": "eFiling",
                "answer": f'<p>Persons who are registered for DAWSON and who agree to the <strong><a linktype="document" id="{definition_docs["tou.pdf"].id}" target="_blank" title="Terms of Use">Terms of Use</a></strong>, consent to eService, and are in good standing with the Court may electronically file (eFile) documents. For more information, petitioners (taxpayers) should consult the <strong>DAWSON Self-Represented (Pro Se) Training Guide</strong>. Counsel admitted to practice before the Tax Court should consult the <strong>DAWSON Practitioner Training Guide</strong>.</p>',
            },
            {
                "question": "EITC",
                "answer": "<p>Earned Income Tax Credit.</p>",
            },
            {
                "question": "eLodged",
                "answer": '<p>"eLodged" refers to any document that is electronically submitted to the Court with a motion for leave through DAWSON and that is not automatically filed.</p>',
            },
            {
                "question": "Examination of the Return",
                "answer": "<p>See Audit.</p>",
            },
            {
                "question": "Innocent Spouse Case",
                "answer": "<p>A case where the taxpayer seeks relief from joint and several liability under the provisions of I.R.C. section 6015.</p>",
            },
            {
                "question": "Intervenor / Participant",
                "answer": f'<p>"Intervenor" is a third party who has an interest in the outcome of the case. The most common example is the spouse or former spouse of a petitioner seeking innocent spouse relief. "Participant" is a partner who elects to participate in a partnership action by filing a notice of election to participate under <a linktype="document" id="{definition_docs["rule-245.pdf"].id}"><b>Rule 245</b></a>.</p>',
            },
            {
                "question": "I.R.C.",
                "answer": "<p>Internal Revenue Code.</p>",
            },
            {
                "question": "IRS",
                "answer": "<p>Internal Revenue Service. The IRS Web site is <a href='https://www.irs.gov/'>www.irs.gov</a>.</p>",
            },
            {
                "question": "Jurisdiction",
                "answer": "<p>The Court's authority to hear your case. For example, a taxpayer must file a petition with the Court within the time provided by the Internal Revenue Code after the notice of deficiency or notice of determination is issued for the Court to have jurisdiction. Also, in most circumstances, a taxpayer must have been sent a notice of deficiency or notice of determination for the Court to have jurisdiction to consider the case.</p>",
            },
            {
                "question": "Lien/Levy Case",
                "answer": "<p>See CDP.</p>",
            },
            {
                "question": "LITC",
                "answer": "<p>Low Income Taxpayer Clinic. LITCs serve taxpayers meeting certain income guidelines all across the country. A <strong><a href='/clinics' title='Clinics'>list of LITCs</a></strong> can be found on the Tax Court Website.</p>",
            },
            {
                "question": "Memorandum of Authority",
                "answer": "<p>A written statement of the legal authorities supporting a position taken at trial.</p>",
            },
            {
                "question": "Motion",
                "answer": "<p>One or both parties can file a written request for the Court to take some action. Such a request is known as a motion. For example, if the petitioner wants to continue the trial of a case to another trial date, the petitioner would file a written motion for continuance. Before filing a motion a party should talk to the other party to see if they object to the motion and the motion should indicate where there is any objection. A party may also make an oral motion at a trial session.</p>",
            },
            {
                "question": "Motion for Continuance",
                "answer": "<p>A request (informal or in writing) made to the Court in advance of trial requesting the Court's permission to reschedule the case for a later trial date.</p>",
            },
            {
                "question": "Notice of Deficiency",
                "answer": "<p>The letter from the IRS informing a taxpayer of any tax, additions, and penalties being imposed. Taxpayers generally have 90 days from the date the IRS mails the Notice of Deficiency to petition the Tax Court.</p>",
            },
            {
                "question": "Notice of Determination",
                "answer": "<p>The letter sent by the IRS to a taxpayer informing them of the IRS's decision in a collection review case, an innocent spouse case, or the review of a worker classification. In collection review cases, taxpayers generally have 30 days from the date the IRS mails the Notice of Determination to petition the Tax Court.</p>",
            },
            {
                "question": "Notice Setting Case for Trial",
                "answer": "<p>A notice sent by the Court to all parties in a case informing them of the date, time, and place of their trial.</p>",
            },
            {
                "question": "Party",
                "answer": '<p>"Party", for purposes of electronic access, means either petitioner(s) or respondent (IRS).</p>',
            },
            {
                "question": "Passport Certification",
                "answer": f'<p>Passport certification actions are commenced with respect to notices of certification issued under I.R.C. section 7345, Revocation or Denial of Passport in Case of Certain Tax Delinquencies, effective after December 4, 2015. See also <strong><a linktype="document" id="{definition_docs["rule-350.pdf"].id}" target="_blank" title="Tax Court Rule 350">Tax Court Rule 350</a></strong> et seq. regarding Certification and Failure to Reverse Certification Action with Respect to Passports. A passport case has a docket number ending in "P", for example, 77899-17P.</p>',
            },
            {
                "question": "PDF",
                "answer": '<p>"PDF" means Portable Document Format. Documents in PDF may be opened in Adobe Reader or an equivalent viewer. Adobe Reader may be downloaded free of charge from the Adobe website (www.adobe.com). Electronic documents may be converted to PDF through a word processor, third party PDF creation software such as Adobe Acrobat, or online PDF creation services from Adobe (<a href="https://createpdf.adobe.com/">https://createpdf.adobe.com/</a>) and others. Documents in paper form may be scanned into PDF.</p>',
            },
            {
                "question": "Petition",
                "answer": f'<p>The document a taxpayer files (along with a copy of a Notice of Deficiency or Notice of Determination) explaining to the Court why they disagree with the Internal Revenue Service. A case cannot be heard without a timely filed <strong><a linktype="document" id="{definition_docs["Petition_Kit.pdf"].id}" target="_blank" title="petition">petition</a></strong>.</p>',
            },
            {
                "question": "Petitioner",
                "answer": "<p>The taxpayer bringing a case before the Tax Court.</p>",
            },
            {
                "question": "Place of Trial",
                "answer": f'<p>The <strong><a linktype="document" id="{definition_docs["Form_5_Request_for_Place_of_Trial.pdf"].id}" target="_blank" title="Request for Place of Trial">Request for Place of Trial</a></strong> (Form 5) and the <a href="/petitioners">Guidance for Petitioners</a> tab on the Court\'s Web site provide a list of cities at which the Court holds trials. Trials of S cases are held in several additional cities.</p>',
            },
            {
                "question": "Pleadings",
                "answer": "<p>The pleadings are the petition and answer and, where required under the Rules, a reply.</p>",
            },
            {
                "question": "Pretrial Memorandum",
                "answer": f'<p>A written document submitted to the Court by each party providing a brief summary of their case. Petitioners may use the form provided <strong><a linktype="document" id="{definition_docs["Pretrial_Memorandum_Form_old.pdf"].id}" target="_blank" title="here">here</a></strong>.</p>',
            },
            {
                "question": "Pro Se",
                "answer": '<p>"Pro Se" means a petitioner who represents themselves without a lawyer or an entity appearing through an authorized fiduciary or officer.</p>',
            },
            {
                "question": "Record",
                "answer": "<p>All of the documents and evidence (including testimony) that the Judge will consider when deciding a case.</p>",
            },
            {
                "question": "Regular Tax Case",
                "answer": "<p>A case in which the taxpayer elects not to be heard under the Small Tax Case procedures. The differences between a regular tax case and small tax case are described in the <a href='/petitioners-start#START12'>Guidance for Petitioners</a> section of the Tax Court Web site and in the informational packet available from the Court.</p>",
            },
            {
                "question": "Reply",
                "answer": f'<p>In some limited circumstances a petitioner is required to respond to respondent\'s answer. A petitioner has 45 days from the date of service of the answer within which to file a reply if one is required. <strong><a linktype="document" id="{definition_docs["rule-37.pdf"].id}" target="_blank" title="Rule 37">Rule 37</a></strong> and <strong><a linktype="document" id="{definition_docs["rule-173.pdf"].id}" target="_blank" title="Rule 173">Rule 173</a></strong>.</p>',
            },
            {
                "question": "Request for Place of Trial",
                "answer": f'<p>This document (<strong><a linktype="document" id="{definition_docs["Form_5_Request_for_Place_of_Trial.pdf"].id}" target="_blank" title="Tax Court Form 5">Tax Court Form 5</a></strong>) is filed with a petition and asks the Court for a trial in a particular city.</p>',
            },
            {
                "question": "Respondent",
                "answer": "<p>The Internal Revenue Service is always the respondent in Tax Court cases.</p>",
            },
            {
                "question": "Rules",
                "answer": "<p>Refers to the <a href='/rules'>Tax Court Rules of Practice and Procedure</a>. The complete set of Tax Court Rules is located under the <a href='/rules'>Rules</a> page on the Tax Court's Web site.</p>",
            },
            {
                "question": "Small Tax Case (S Case)",
                "answer": "<p>An \"S\" case is heard under less formal procedures and there is no right of appeal. Cases may not exceed certain monetary thresholds (generally $50,000 per year in issue) in order to be heard as a small tax case. For more information, please refer to the <a href='/petitioners-start#START12'>Guidance for Petitioners</a> section of the Tax Court Website.</p>",
            },
            {
                "question": "Standing Pretrial Notice (SPTN)",
                "answer": "<p>A notice sent by the Court in advance of a small tax case trial instructing the petitioner on the procedures before and during trial.</p>",
            },
            {
                "question": "Standing Pretrial Order (SPTO)",
                "answer": "<p>A notice sent by the Court in advance of a small tax case trial instructing the petitioner on the procedures before and during trial.</p>",
            },
            {
                "question": "Statement of Taxpayer Identification Number",
                "answer": f'<p>A document (<strong><a linktype="document" id="{definition_docs["Form_4_Statement_of_Taxpayer_Identification_Number.pdf"].id}" target="_blank" title="Tax Court Form 4">Tax Court Form 4</a></strong>) submitted with a petition providing the taxpayer\'s name and Social Security (or other taxpayer ID) number; this document is not filed or made available to the public.</p>',
            },
            {
                "question": "Stipulated Decision",
                "answer": '<p>A decision drafted and signed by the parties when a case is settled. The "stip decision" is then reviewed by the Court and, if acceptable, entered in lieu of trial.</p>',
            },
            {
                "question": "Stipulation of Facts",
                "answer": "<p>A document signed by both the petitioner and the respondent outlining relevant facts of the case not in dispute. Copies of documents or other materials not in dispute are usually attached as exhibits.</p>",
            },
            {
                "question": "Subpoena",
                "answer": f'<p>A command by the Court for a witness to produce documents or provide testimony at trial or deposition. <strong><a linktype="document" id="{definition_docs["Subpoena_Appear_Testify_Hearing_Or_Trial.pdf"].id}" target="_blank" title="Subpoena to Appear and Testify at a Hearing or Trial (Form 14A)">Subpoena to Appear and Testify at a Hearing or Trial (Form 14A)</a></strong> and <strong><a linktype="document" id="{definition_docs["Subpoena_To_Testify_Deposition.pdf"].id}" target="_blank" title="Subpoena to Testify at a Deposition (Form 14B)">Subpoena to Testify at a Deposition (Form 14B)</a></strong> are available on the Court\'s Web site. A petitioner must pay fees and expenses to the witness. The $40 attendance fee is subject to change, and you should look to 26 U.S.C. section 1821 for amendments. The relevant regulations for travel expenses appear at 41 C.F.R. section 301-10 (also subject to amendment); and the mileage rate, currently $0.655 per mile, is updated at <a href="http://www.gsa.gov/mileage">http://www.gsa.gov/mileage</a>.</p>',
            },
            {
                "question": "Trier of Fact",
                "answer": "<p>In Tax Court cases, the presiding Judge is always the trier of fact.</p>",
            },
        ]

        # Create definition blocks
        definitions = []
        for definition in all_definitions:
            definitions.append(
                {
                    "type": "definition",
                    "value": {
                        "question": definition["question"],
                        "answer": definition["answer"],
                    },
                }
            )

        new_page = home_page.add_child(
            instance=DefinitionsPage(
                title=title,
                slug=self.slug,
                seo_title=title,
                search_description="Definitions and Glossary of terms for Tax Court and DAWSON",
                definitions=definitions,
            )
        )

        new_page.save_revision().publish()
        logger.info(
            f"Created the '{title}' page with {len(all_definitions)} definitions."
        )
