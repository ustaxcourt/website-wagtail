from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage


petitioners_docs = {
    "Form_4_Statement_of_Taxpayer_Identification_Number.pdf": "",
    "Form_5_Request_for_Place_of_Trial.pdf": "",
    "Petition_Kit.pdf": "",
    "Pretrial_Memorandum_Form_old.pdf": "",
    "Rule-37.pdf": "",
    "Rule-151.pdf": "",
    "Rule-173.pdf": "",
    "Rule-280(amended).pdf": "",
    "Rule-350.pdf": "",
    "Subpoena_Appear_Testify_Hearing_Or_Trial.pdf": "",
    "Subpoena_To_Testify_Deposition.pdf": "",
    "tou.pdf": "",
}


class PetitionersGlossaryPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners_glossary"
        title = "Guidance for Petitioners: Glossary"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        for document in petitioners_docs.keys():
            uploaded_document = self.load_document_from_documents_dir(
                "petitioners_glossary", document
            )
            petitioners_docs[document] = uploaded_document.file.url

        questions = [
            {
                "question": "Abatement",
                "answer": f'Abatement cases ask the IRS to lessen the amount of interest owed when certain requirements are met. See I.R.C. section 6404 and <strong><a href="{petitioners_docs["Rule-280(amended).pdf"]}" target="_blank" title="Tax Court Rule 280">Tax Court Rule 280</a></strong> et seq. regarding Actions for Review of Failure to Abate Interest.',
                "anchortag": "ABATEMENT",
            },
            {
                "question": "Answer",
                "answer": "The document respondent files in response to a petition, admitting or denying each allegation in the petition.",
                "anchortag": "ANSWER",
            },
            {
                "question": "Appeals Court",
                "answer": "Generally, regular cases may be appealed (by either party) to the United States Court of Appeals for the circuit in which the petitioner lived when the petition was filed.",
                "anchortag": "APPEALS_COURT",
            },
            {
                "question": "Appeals Office",
                "answer": "References to the Appeals Office are usually to the IRS Independent Office of Appeals. Similarly, an Appeals Officer works in that office.",
                "anchortag": "APPEALS_OFFICE",
            },
            {
                "question": "At issue",
                "answer": f'A case is deemed "at issue" once the petition and answer have been filed. In some very limited circumstances where a reply is required, the case will be at issue after a reply to the answer is filed. See <strong><a href="{petitioners_docs["Rule-37.pdf"]}" target="_blank" title="Rules 37">Rules 37</a></strong> or <strong><a href="{petitioners_docs["Rule-173.pdf"]}" target="_blank" title="173">173</a></strong>.',
                "anchortag": "AT_ISSUE",
            },
            {
                "question": "Audit",
                "answer": "Although there are different types of audits, an audit is an examination of one’s tax returns for a given year or series of years by the IRS.",
                "anchortag": "AUDIT",
            },
            {
                "question": "Bench Opinion",
                "answer": "An oral opinion rendered by the Judge at the close of trial.",
                "anchortag": "BENCH_OPINION",
            },
            {
                "question": "Brief",
                "answer": f'A brief is a formal document normally filed by each party after the trial in a regular case. A brief contains a table of contents, a statement of the issues, proposed findings of facts, points of law relied upon, argument and analysis. See <strong><a href="{petitioners_docs["Rule-151.pdf"]}" target="_blank" title="Rule 151">Rule 151</a></strong>.',
                "anchortag": "BRIEF",
            },
            {
                "question": "Burden of Proof",
                "answer": "The taxpayer who is asking the Court to change the IRS’s determination must present evidence to the Court which will support his/her position, and must persuade the Judge that the evidence supports the taxpayer’s position.",
                "anchortag": "BURDEN_OF_PROOF",
            },
            {
                "question": "Calendar Call",
                "answer": "Calendar call occurs on the first day of a trial session (normally Monday) and provides the Judge with the opportunity to ensure that all cases listed on the docket are ready for trial or other disposition. All parties are required to attend unless specifically excused.",
                "anchortag": "CALENDAR_CALL",
            },
            {
                "question": "Caption",
                "answer": "The caption refers to the name of the parties (e.g., Dan & Susan Smith, Petitioners v. Commissioner of Internal Revenue, Respondent).",
                "anchortag": "CAPTION",
            },
            {
                "question": "CDP",
                "answer": "Collection Due Process (CDP) refers to cases in which the collection of taxes is being made by IRS lien or levy under I.R.C. sections 6320 and/or 6330. A CDP case has a docket number ending in “L”, for example, 77899-14L.",
                "anchortag": "CDP",
            },
            {
                "question": "Certificate of Service",
                "answer": "A “Certificate of Service” is used to show that you have sent or delivered documents to another party, typically the opposing counsel.",
                "anchortag": "CERTIFICATE_OF_SERVICE",
            },
            {
                "question": "Collection Review Case",
                "answer": "See CDP.",
                "anchortag": "COLLECTION_REVIEW_CASE",
            },
            {
                "question": "DAWSON",
                "answer": "The Court's case management system. <a href='/dawson'>Find out more</a>.",
                "anchortag": "DAWSON",
            },
            {
                "question": "Decision",
                "answer": "A decision document closes a case. A decision is signed by a Judge and entered in the Court’s record. The decision reflects the conclusions of the Court. A decision can be entered in a case after the parties have settled all issues or the Judge has issued an opinion or order deciding all issues in a case.",
                "anchortag": "DECISION",
            },
            {
                "question": "Discovery",
                "answer": "The parties can seek to obtain information and documents necessary to present their case. “Interrogatories” are written questions asked of the opposing party and a “request for documents” is a request to obtain documents and records. Before making a formal request for interrogatories or documents, the parties should talk with one another and make an informal request.",
                "anchortag": "DISCOVERY",
            },
            {
                "question": "Docket Number",
                "answer": "A multi-digit number the Court assigns to each case for tracking purposes. The last two digits represent the year in which the petition was filed. Small Tax Case docket numbers always end in S.",
                "anchortag": "DOCKET_NUMBER",
            },
            {
                "question": "eFiling",
                "answer": f'Persons who are registered for DAWSON and who agree to the <strong><a href="{petitioners_docs["tou.pdf"]}" target="_blank" title="Terms of Use">Terms of Use</a></strong>, consent to eService, and are in good standing with the Court may electronically file (eFile) documents. For more information, petitioners (taxpayers) should consult the <strong>DAWSON Self-Represented (Pro Se) Training Guide</strong>. Counsel admitted to practice before the Tax Court should consult the <strong>DAWSON Practitioner Training Guide</strong>.',
                "anchortag": "EFILING",
            },
            {
                "question": "EITC",
                "answer": "Earned Income Tax Credit.",
                "anchortag": "EITC",
            },
            {
                "question": "Examination of the Return",
                "answer": "See Audit.",
                "anchortag": "EXAMINATION_OF_THE_RETURN",
            },
            {
                "question": "Innocent Spouse Case",
                "answer": "A case where the taxpayer seeks relief from joint and several liability under the provisions of I.R.C. section 6015.",
                "anchortag": "INNOCENT_SPOUSE_CASE",
            },
            {
                "question": "Intervenor",
                "answer": "The non-requesting spouse in a section 6015 (“Innocent Spouse”) case.",
                "anchortag": "INTERVENOR",
            },
            {
                "question": "I.R.C.",
                "answer": "Internal Revenue Code.",
                "anchortag": "IRC",
            },
            {
                "question": "IRS",
                "answer": "Internal Revenue Service. The IRS Web site is <a href='https://www.irs.gov/'>www.irs.gov</a>.",
                "anchortag": "IRS",
            },
            {
                "question": "Jurisdiction",
                "answer": "The Court’s authority to hear your case. For example, a taxpayer must file a petition with the Court within the time provided by the Internal Revenue Code after the notice of deficiency or notice of determination is issued for the Court to have jurisdiction. Also, in most circumstances, a taxpayer must have been sent a notice of deficiency or notice of determination for the Court to have jurisdiction to consider the case.",
                "anchortag": "JURISDICTION",
            },
            {
                "question": "Lien/Levy Case",
                "answer": "See CDP.",
                "anchortag": "LIEN_LEVY_CASE",
            },
            {
                "question": "LITC",
                "answer": "Low Income Taxpayer Clinic. LITCs serve taxpayers meeting certain income guidelines all across the country. A <strong>list of LITCs</strong> can be found on the Tax Court Website.",
                "anchortag": "LITC",
            },
            {
                "question": "Memorandum of Authority",
                "answer": "A written statement of the legal authorities supporting a position taken at trial.",
                "anchortag": "MEMORANDUM_OF_AUTHORITY",
            },
            {
                "question": "Motion",
                "answer": "One or both parties can file a written request for the Court to take some action. Such a request is known as a motion. For example, if the petitioner wants to continue the trial of a case to another trial date, the petitioner would file a written motion for continuance. Before filing a motion a party should talk to the other party to see if they object to the motion and the motion should indicate where there is any objection. A party may also make an oral motion at a trial session.",
                "anchortag": "MOTION",
            },
            {
                "question": "Motion for Continuance",
                "answer": "A request (informal or in writing) made to the Court in advance of trial requesting the Court’s permission to reschedule the case for a later trial date.",
                "anchortag": "MOTION_FOR_CONTINUANCE",
            },
            {
                "question": "Notice of Deficiency",
                "answer": "The letter from the IRS informing a taxpayer of any tax, additions, and penalties being imposed. Taxpayers generally have 90 days from the date the IRS mails the Notice of Deficiency to petition the Tax Court.",
                "anchortag": "NOTICE_OF_DEFICIENCY",
            },
            {
                "question": "Notice of Determination",
                "answer": "The letter sent by the IRS to a taxpayer informing them of the IRS’s decision in a collection review case, an innocent spouse case, or the review of a worker classification. In collection review cases, taxpayers generally have 30 days from the date the IRS mails the Notice of Determination to petition the Tax Court.",
                "anchortag": "NOTICE_OF_DETERMINATION",
            },
            {
                "question": "Notice Setting Case for Trial",
                "answer": "A notice sent by the Court to all parties in a case informing them of the date, time, and place of their trial.",
                "anchortag": "NOTICE_SETTING_CASE_FOR_TRIAL",
            },
            {
                "question": "Passport Certification",
                "answer": f'Passport certification actions are commenced with respect to notices of certification issued under I.R.C. section 7345, Revocation or Denial of Passport in Case of Certain Tax Delinquencies, effective after December 4, 2015. See also <strong><a href="{petitioners_docs["Rule-350.pdf"]}" target="_blank" title="Tax Court Rule 350">Tax Court Rule 350</a></strong> et seq. regarding Certification and Failure to Reverse Certification Action with Respect to Passports. A passport case has a docket number ending in "P", for example, 77899-17P.',
                "anchortag": "PASSPORT_CERTIFICATION",
            },
            {
                "question": "Petition",
                "answer": f'The document a taxpayer files (along with a copy of a Notice of Deficiency or Notice of Determination) explaining to the Court why they disagree with the Internal Revenue Service. A case cannot be heard without a timely filed <strong><a href="{petitioners_docs["Petition_Kit.pdf"]}" target="_blank" title="petition">petition</a></strong>.',
                "anchortag": "PETITION",
            },
            {
                "question": "Petitioner",
                "answer": "The taxpayer bringing a case before the Tax Court.",
                "anchortag": "PETITIONER",
            },
            {
                "question": "Place of Trial",
                "answer": f'The <strong><a href="{petitioners_docs["Form_5_Request_for_Place_of_Trial.pdf"]}" target="_blank" title="Request for Place of Trial">Request for Place of Trial</a></strong> (Form 5) and the <a href="/petitioners">Guidance for Petitioners</a> tab on the Court’s Web site provide a list of cities at which the Court holds trials. Trials of S cases are held in several additional cities.',
                "anchortag": "PLACE_OF_TRIAL",
            },
            {
                "question": "Pleadings",
                "answer": "The pleadings are the petition and answer and, where required under the Rules, a reply.",
                "anchortag": "PLEADINGS",
            },
            {
                "question": "Pretrial Memorandum",
                "answer": f'A written document submitted to the Court by each party providing a brief summary of their case. Petitioners may use the form provided <strong><a href="{petitioners_docs["Pretrial_Memorandum_Form_old.pdf"]}" target="_blank" title="here">here</a></strong>.',
                "anchortag": "PRETRIAL_MEMORANDUM",
            },
            {
                "question": "Pro Se",
                "answer": "A petitioner who represents himself or herself.",
                "anchortag": "PRO_SE",
            },
            {
                "question": "Record",
                "answer": "All of the documents and evidence (including testimony) that the Judge will consider when deciding a case.",
                "anchortag": "RECORD",
            },
            {
                "question": "Regular Tax Case",
                "answer": "A case in which the taxpayer elects not to be heard under the Small Tax Case procedures. The differences between a regular tax case and small tax case are described in the <a href='/petitioners_start#START12'>Guidance for Petitioners</a> section of the Tax Court Web site and in the informational packet available from the Court.",
                "anchortag": "REGULAR_TAX_CASE",
            },
            {
                "question": "Reply",
                "answer": f'In some limited circumstances a petitioner is required to respond to respondent’s answer. A petitioner has 45 days from the date of service of the answer within which to file a reply if one is required. <strong><a href="{petitioners_docs["Rule-37.pdf"]}" target="_blank" title="Rule 37">Rule 37</a></strong> and <strong><a href="{petitioners_docs["Rule-173.pdf"]}" target="_blank" title="Rule 173">Rule 173</a></strong>.',
                "anchortag": "REPLY",
            },
            {
                "question": "Request for Place of Trial",
                "answer": f'This document (<strong><a href="{petitioners_docs["Form_5_Request_for_Place_of_Trial.pdf"]}" target="_blank" title="Tax Court Form 5">Tax Court Form 5</a></strong>) is filed with a petition and asks the Court for a trial in a particular city.',
                "anchortag": "REQUEST_FOR_PLACE_OF_TRIAL",
            },
            {
                "question": "Respondent",
                "answer": "The Internal Revenue Service is always the respondent in Tax Court cases.",
                "anchortag": "RESPONDENT",
            },
            {
                "question": "Rules",
                "answer": "Refers to the <a href='/rules'>Tax Court Rules of Practice and Procedure</a>. The complete set of Tax Court Rules is located under the <a href='/rules'>Rules</a> page on the Tax Court’s Web site.",
                "anchortag": "RULES",
            },
            {
                "question": "Small Tax Case (S Case)",
                "answer": "An “S” case is heard under less formal procedures and there is no right of appeal. Cases may not exceed certain monetary thresholds (generally $50,000 per year in issue) in order to be heard as a small tax case. For more information, please refer to the <a href='/petitioners_start#START12'>Guidance for Petitioners</a> section of the Tax Court Website.",
                "anchortag": "SMALL_TAX_CASE",
            },
            {
                "question": "Standing Pretrial Notice (SPTN)",
                "answer": "A notice sent by the Court in advance of a small tax case trial instructing the petitioner on the procedures before and during trial.",
                "anchortag": "SPTN",
            },
            {
                "question": "Standing Pretrial Order (SPTO)",
                "answer": "A notice sent by the Court in advance of a small tax case trial instructing the petitioner on the procedures before and during trial.",
                "anchortag": "SPTO",
            },
            {
                "question": "Statement of Taxpayer Identification Number",
                "answer": f'A document (<strong><a href="{petitioners_docs["Form_4_Statement_of_Taxpayer_Identification_Number.pdf"]}" target="_blank" title="Tax Court Form 4">Tax Court Form 4</a></strong>) submitted with a petition providing the taxpayer’s name and Social Security (or other taxpayer ID) number; this document is not filed or made available to the public.',
                "anchortag": "STIN",
            },
            {
                "question": "Stipulated Decision",
                "answer": "A decision drafted and signed by the parties when a case is settled. The “stip decision” is then reviewed by the Court and, if acceptable, entered in lieu of trial.",
                "anchortag": "STIPULATED_DECISION",
            },
            {
                "question": "Stipulation of Facts",
                "answer": "A document signed by both the petitioner and the respondent outlining relevant facts of the case not in dispute. Copies of documents or other materials not in dispute are usually attached as exhibits.",
                "anchortag": "STIPULATION_OF_FACTS",
            },
            {
                "question": "Subpoena",
                "answer": f'A command by the Court for a witness to produce documents or provide testimony at trial or deposition. <strong><a href="{petitioners_docs["Subpoena_Appear_Testify_Hearing_Or_Trial.pdf"]}" target="_blank" title="Subpoena to Appear and Testify at a Hearing or Trial (Form 14A)">Subpoena to Appear and Testify at a Hearing or Trial (Form 14A)</a></strong> and <strong><a href="{petitioners_docs["Subpoena_To_Testify_Deposition.pdf"]}" target="_blank" title="Subpoena to Testify at a Deposition (Form 14B)">Subpoena to Testify at a Deposition (Form 14B)</a></strong> are available on the Court’s Web site. A petitioner must pay fees and expenses to the witness. The $40 attendance fee is subject to change, and you should look to 26 U.S.C. section 1821 for amendments. The relevant regulations for travel expenses appear at 41 C.F.R. section 301-10 (also subject to amendment); and the mileage rate, currently $0.655 per mile, is updated at <a href="http://www.gsa.gov/mileage">http://www.gsa.gov/mileage</a>.',
                "anchortag": "SUBPOENA",
            },
            {
                "question": "Trier of Fact",
                "answer": "In Tax Court cases, the presiding Judge is always the trier of fact.",
                "anchortag": "TRIER_OF_FACT",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Guidance for Petitioners - Glossary",
                body=[
                    {"type": "h2", "value": "Glossary"},
                    {"type": "questionanswers", "value": questions},
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
