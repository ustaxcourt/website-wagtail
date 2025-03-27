from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage

petitioners_docs = {
    "Rule-74(amended).pdf": "",
    "Rule-81.pdf": "",
    "Rule-147.pdf": "",
    "Rule-148.pdf": "",
    "Sample_Notice_Setting_Case_for_Trial_R_cases.pdf": "",
    "Sample_Notice_Setting_Case_for_Trial_S_cases.pdf": "",
    "SPTO_regular_sample.pdf": "",
    "SPTO_small_sample.pdf": "",
    "Subpoena_Appear_Testify_Hearing_Or_Trial.pdf": "",
    "Subpoena_To_Testify_Deposition.pdf": "",
}


class PetitionersBeforeTrialInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners-before"
        title = "Guidance for Petitioners: Things That Occur Before Trial"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        for document in petitioners_docs.keys():
            uploaded_document = self.load_document_from_documents_dir(None, document)
            petitioners_docs[document] = uploaded_document.file.url

        questions = [
            {
                "question": "After I get my docket number, when will I have my trial?",
                "answer": """You will not have a trial immediately. A few things will occur before the trial.
                            <br>
                            <br>
                                    <ol>
                                       <li>
                                           The IRS attorney will file an “Answer” with the Court and serve a copy on you by mail if you are not yet registered for electronic filing. In the Answer, the IRS will generally admit or deny the statements made in your petition. Sometimes the Answer will indicate that the IRS does not have enough information to admit or deny what has been said in the petition. The purpose of the Answer is to have the IRS respond to your petition and let you and the Court know what the disagreements are between the taxpayer and the IRS. Most importantly, the Answer will contain the name, address, and telephone number of the attorney from the IRS whom you may contact about your case.
                                       </li>
                                       <li>
                                           An IRS employee will contact you after the Answer is filed to schedule a conference or meeting. Your case may be scheduled for trial as soon as six months after the Answer is filed but it may take longer. If you do not hear from the IRS, you may call or write the IRS and have a conference in person or by telephone. One of the reasons for the conference or meeting is to try to come to an agreement (settlement) on some or all of the issues in your case and stipulate (agree) to facts. You should participate in any scheduled meetings and bring to the meetings all documents that may help you to support your position on the items in question.
                                       </li>
                                       <li>
                                           If you settle your case with the IRS, a settlement document (stipulated decision) will be prepared by the IRS. If you agree with the settlement document, sign it and send it back to the IRS. The IRS attorney will also sign the stipulated decision and then send it to the Tax Court. The Tax Court will enter the decision into the official record and send you a copy of the entered decision. If this occurs before the trial date of your case, you will not be required to appear in court.
                                       </li>
                                   </ol>""",
                "anchortag": "START1",
            },
            {
                "question": "What happens if I don’t settle my case before trial?",
                "answer": """You should meet or talk with the IRS representative to see whether you can agree to (stipulate) facts and documents that will be offered to convince the Judge that you are correct. You should enter into a stipulation of facts (a formal written document in which you and the IRS representative agree to facts and documents).
                             <br>
                             <br>
                             The stipulation of facts is usually a typewritten document that results from conversations between you and the IRS attorney. For example, some of the things you should be able to agree to are:
                             <br>
                             <br>
                                <ol>
                                    <li>A copy of the tax return(s);</li>
                                    <li>a copy of the notice of deficiency, the notice of determination, or the notice of certification;</li>
                                    <li>copies of agreements or contracts (if any) that concern the items in dispute; and</li>
                                    <li>copies of canceled checks, receipts, or invoices (if any) that concern the items in dispute.</li>
                                </ol>
                            It helps everyone to stipulate facts and documents that the parties agree are not in dispute.
                            <br>
                            <br>
                            You can also stipulate issues that you have settled with the IRS.""",
                "anchortag": "START2",
            },
            {
                "question": "How can I obtain evidence to prove my case?",
                "answer": "Because a taxpayer’s tax liability usually turns on the taxpayer’s own activities, transactions, and expenditures, the evidence in many Tax Court trials consists simply of the petitioner’s own testimony and documents. Where the documents of a third party are needed, they are most often obtained by informal requests; and where a third party’s testimony is needed, it is usually obtained simply by asking the person to appear as a witness. However, if a third party refuses to cooperate, then a subpoena may be used to compel the person to appear at the trial.",
                "anchortag": "START3",
            },
            {
                "question": "What is a subpoena?",
                "answer": f'A subpoena is an order issued by the Tax Court (1) directing a person to appear and testify at a scheduled Tax Court Trial Session or (2) directing a person to appear at a deposition prearranged at a specific time and location. The subpoena may include directions for the person (witness) to produce specific books, papers, documents, electronically stored information, or tangible things. See Tax Court Rules <strong><a href="{petitioners_docs["Rule-147.pdf"]}" target="_blank" title="Rule 147">147</a>,<a href="{petitioners_docs["Rule-74(amended).pdf"]}" target="_blank" title="Rule 74">74</a></strong> and <strong><a href="{petitioners_docs["Rule-81.pdf"]}" target="_blank" title="Rule 81">81</a></strong>.',
                "anchortag": "START4",
            },
            {
                "question": "When is it appropriate to use a Tax Court subpoena?",
                "answer": 'If you can’t get documents you need for Court and/or you need a witness to testify at a deposition or at trial, you can consider serving a subpoena. Most often, the parties agree to documents in the stipulation process and you don’t need a subpoena. (<strong><a href="#START2">See the discussion above about stipulation of facts</a></strong>). Sometimes, however, documents are not readily available or a witness is uncooperative, and a subpoena may be needed to get a witness to testify or to produce a document to assist you in proving your case.',
                "anchortag": "START5",
            },
            {
                "question": "How do I obtain and serve a Tax Court subpoena?",
                "answer": f"""You may obtain a form for a <strong><a href="{petitioners_docs["Subpoena_Appear_Testify_Hearing_Or_Trial.pdf"]}" target="_blank" title="Subpoena to Appear and Testify at a Hearing or Trial (Form 14A)">Subpoena to Appear and Testify at a Hearing or Trial (Form 14A)
                            </a></strong> or a <strong><a href="{petitioners_docs["Subpoena_To_Testify_Deposition.pdf"]}" target="_blank" title="Subpoena to Testify at a Deposition (Form 14B)">Subpoena to Testify at a Deposition (Form 14B)</a>
                           </strong> under the <strong><a href="/case-related-forms" title="Case Related Forms">“Forms”</a>
                           </strong> tab on the Court’s internet website.You may also obtain a copy of subpoena form 14A from a trial clerk at a trial session.
                           <br>
                           <br>
                           After the top portion of the subpoena form is completed, a copy of the subpoena must be
                           served on the witness, in person, by a United States marshal, a deputy marshal, or by any
                           other person who is not a party to the case and who is not less than 18 years of age.
                           The person who actually serves the subpoena must complete the “Return of Service” section
                           at the bottom of the subpoena form. See <strong><a href="{petitioners_docs["Rule-147.pdf"]}" target="_blank" title="Rule 147">Tax Court Rule 147(c)</a></strong>.
                           You will submit the signed original to the Court only if it is necessary to ask the Court to enforce the subpoena.""",
                "anchortag": "START6",
            },
            {
                "question": "Is there a cost related to a subpoena?",
                "answer": f'Yes. If you as a petitioner are serving a subpoena on a witness, you must pay fees to the witness in advance equal to one day’s attendance and mileage. See <strong><a href="{petitioners_docs["Rule-147.pdf"]}" title="Rule 147">Tax court Rule 147(c)</a></strong>. These fees must be paid to the witness when the subpoena is served. A witness is entitled to the same fees for attendance and transportation as witnesses in the United States District Courts. See <strong><a href="{petitioners_docs["Rule-148.pdf"]}" title="Rule 148">Tax court Rule 148</a></strong>. For more detail as to the amount of the fees and travel allowances go to the definition of Subpoena in the <strong><a href="/petitioners-glossary" title="Glossary">Glossary</a></strong>.',
                "anchortag": "START7",
            },
            {
                "question": "Is it possible to serve a subpoena without paying fees and mileage if I only want a person to mail documents to me?",
                "answer": "No. A subpoena directs a witness to appear at a Tax Court trial session or at a prearranged deposition, and may or may not include a request for books, papers, or documents. You should first attempt to obtain the documents that you need through informal means (e.g., by telephone call or letter). If you believe that you cannot obtain the documents without a subpoena, you will be obliged to pay the fees described above.",
                "anchortag": "START8",
            },
            {
                "question": "What should I do if I am served with a subpoena? Can I challenge a subpoena?",
                "answer": f'As a general matter you should comply with a subpoena. If you are served with a subpoena, and you believe it was issued in error, is unreasonable or oppressive, or was not properly served, you may file a Motion To Quash the subpoena with the Court. If you fail to appear as directed by a subpoena, you may be found to be in contempt of Court. See <strong><a href="{petitioners_docs["Rule-147.pdf"]}" target="_blank" title="Rule 147">Rule 147(e)</a></strong>.',
                "anchortag": "START9",
            },
            {
                "question": "How will I know when and where my trial will take place?",
                "answer": f"""The Tax Court will issue either a<strong><a href="{petitioners_docs["Sample_Notice_Setting_Case_for_Trial_S_cases.pdf"]}" target="_blank" title = "Notice for S Cases " > notice
                             for S cases </a></strong>or a <strong><a href="{petitioners_docs["Sample_Notice_Setting_Case_for_Trial_R_cases.pdf"]}" target="_blank" title="Notice for Regular Cases" > notice for regular cases </a></strong>
                             setting your case for trial generally about five months before the trial date.The notice setting the case for trial provides information such as where and when to appear for your trial session.The Tax Court will attempt to schedule the trial at the city requested in your request for place of trial, but if no courtroom is available, the Tax Court may schedule it at a city reasonably nearby.The Tax Court will issue a
                             <strong><a href="{petitioners_docs["SPTO_regular_sample.pdf"]}" target="_blank" title="Standing Pretrial Order" > Standing Pretrial Order </a></strong>
                             in a regular case or a<strong><a href="{petitioners_docs["SPTO_small_sample.pdf"]}" target="_blank" title="Standing Pretrial Order For Small Tax Cases"> Standing Pretrial Order For Small Tax Cases </a></strong>
                             which will inform you what you need to do to prepare for trial.For information specific to remote proceedings, see
                             <strong><a href="/zoomgov" title="Zoomgov Proceedings" > Remote Proceeding Information </a></strong>.""",
                "anchortag": "START10",
            },
            {
                "question": "Will the Court send me any instructions telling me what I should do to prepare for trial?",
                "answer": f"""Yes. The Tax Court will issue a <strong><a href="{petitioners_docs["SPTO_regular_sample.pdf"]}" target="_blank" title="Standing Pretrial Order">Standing Pretrial Order</a></strong> in a regular case or a <strong><a href="{petitioners_docs["SPTO_small_sample.pdf"]}" target="_blank" title="Standing Pretrial Order For Small Tax Cases">Standing Pretrial Order For Small Tax Cases</a></strong>. Read this order or notice from the Tax Court carefully and keep a copy. The Standing Pretrial Order or Notice has very specific instructions about getting ready for trial. One of the provisions of the Standing Pretrial Order (sent to petitioners in regular cases) is that you must file a pretrial memorandum. The Standing Pretrial Notice (sent to petitioners in S cases) states that you should submit a pretrial memorandum. The Court encourages all parties to submit a pretrial memorandum. You should look at the Standing Pretrial Order or Notice and the form attached, which shows what a pretrial memorandum looks like. The pretrial memorandum can be very helpful in organizing and preparing your case. The pretrial memorandum may also help the Judge to understand your position. The Standing Pretrial Notice also tells you what you need to do to settle your case and how to stipulate facts if you do not settle.
            <br>
            <br>
            Depending upon the city in which your trial will take place, the Tax Court may send you a letter from a tax clinic inviting you to talk with one of the clinic’s attorneys or law students. If you qualify on the basis of certain income standards, the clinic may agree to represent you in your trial. Generally there is no fee for this representation. Many petitioners who are represented by a clinic representative are able to settle their cases with the IRS. The tax clinics are not part of the IRS or the Tax Court; they are totally independent and prepared to help you to fairly resolve your tax dispute with the IRS.""",
                "anchortag": "START11",
            },
            {
                "question": "What is a pretrial memorandum? Do I need to prepare one?",
                "answer": f'A pretrial memorandum form is attached as part of the <strong><a href="{petitioners_docs["SPTO_regular_sample.pdf"]}" target="_blank" title="Standing Pretrial Order">Standing Pretrial Order</a></strong> or <strong><a href="{petitioners_docs["SPTO_small_sample.pdf"]}" target="_blank" title="Standing Pretrial Order For Small Tax Cases">Standing Pretrial Order For Small Tax Cases</a></strong>. You must file a pretrial memorandum in a regular case. You should submit a pretrial memorandum in an S case. The Court encourages all parties to file a pretrial memorandum. Preparing the pretrial memorandum may help you in organizing your case and help the Judge to understand your position. Carefully read the instructions in the Standing Pretrial Order or Notice. Follow the form and instructions. Send your pretrial memorandum to the Court, and send a copy to the IRS attorney.',
                "anchortag": "START12",
            },
            {
                "question": "After I have received the notice setting my case for trial in a specific city, should I use the address of the place of trial to contact the Tax Court?",
                "answer": "No. The Tax Court receives all of its mail at the address in Washington, D.C. You should always address mail to: United States Tax Court, 400 Second Street NW, Washington, DC 20217-0002. Keep in mind that, if you send anything by regular mail to the Tax Court in Washington, D.C., within one week before your trial session, it may not be received in time for your trial. You may want to either use a private overnight delivery service or bring the document with you to trial.",
                "anchortag": "START13",
            },
            {
                "question": "Petitioner (Taxpayer) Trial Preparation Check List",
                "answer": """Some of the instructions contained in the Tax Court’s Standing Pretrial Order or Notice are repeated below.
                        <br>
                        <br>
                        <strong>Before you come to Court:</strong>
                        <br>
                        <ul>
                        <li>Think about what facts you want to tell the Judge.</li>
                        <li>Organize any documents you have to support your case.</li>
                        <li>Organize your facts and arguments so you can present your case clearly.</li>
                        <li>Meet with and talk to people at the IRS who call or write to you.</li>
                       <li> Provide to the IRS copies of documents that you intend to use at trial.</li>
                       <li> Agree in writing to facts and documents that are not in dispute.</li>
                       <li> If the IRS will not agree (stipulate) to your documents, bring three copies of each document to court.</li>
                       <li> Consider whether you need any witnesses to support your case.</li>
                       <li> If you need a witness, make sure the witness is available and present in the courtroom at the trial session.</li>
                       <li> Come to court early so you will be ready when your case is called at the calendar call. You may receive a notice from the Court recommending that you arrive at Court by 9:00 a.m. to have the opportunity to meet with clinical and calendar call attorneys. The Court believes it would be in your interest to comply with this recommendation.</li>
                        </ul>""",
                "anchortag": "START14",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Guidance for Petitioners - Things That Occur Before Trial",
                body=[
                    {"type": "h2", "value": "Things That Occur Before Trial"},
                    {"type": "questionanswers", "value": questions},
                ],
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
