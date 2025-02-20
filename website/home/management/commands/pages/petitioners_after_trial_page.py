from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage

petitioners_docs = {
    "Rule-190.pdf": "",
    "Rule-191.pdf": "",
    "Rule-192.pdf": "",
    "Rule-193.pdf": "",
}


class PetitionersAfterTrialInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners_after"
        title = "Guidance for Petitioners: Things That Occur After Trial"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        for document in petitioners_docs.keys():
            uploaded_document = self.load_document_from_documents_dir(
                "petitioners_after", document
            )
            petitioners_docs[document] = uploaded_document.file.url

        questions = [
            {
                "question": "What happens after I finish my trial?",
                "answer": "The Judge may direct the filing of posttrial briefs or may permit the parties to make oral argument or file memoranda or statements of legal authority. A brief is a legal document in which a party presents proposed findings of fact and legal arguments. At the end of the trial, the Judge will tell you what will be required.",
                "anchortag": "START1",
            },
            {
                "question": "When will the Judge decide my case? (When will I find out whether I’ve won or lost my case?)",
                "answer": """<ol>
                               <li>There is no fixed time within which a Judge will decide your case. The Judge might issue an oral opinion (called a Bench Opinion) during the trial session. If a Bench Opinion is not issued, the Judge will return to Washington, D.C., to review the testimony and exhibits in the case and issue an opinion as quickly as practicable.
                               <br>
                               <br>
                               </li>
                               <li>Does the Tax Court issue different types of opinions?</li>
                               <br>
                               Yes. The different kinds of opinions are set forth below.
                               <br>
                               <br>
                               A. <strong>Bench Opinion</strong> - As described above, the Judge may issue a Bench Opinion in a regular or S case during the trial session. In this situation, the Judge orally states the opinion in court during the trial session. The Tax Court will send you a copy of the transcript reflecting the Judge's opinion within a few weeks after the trial. A Bench Opinion cannot be relied on as precedent. All bench opinions delivered after March 1, 2008, are electronically viewable through the Tax Court's Docket Inquiry system.
                               <br>
                               <br>
                               B.<strong>Summary Opinion</strong> - A Summary Opinion is issued in an S case. A Summary Opinion cannot be relied on as precedent, and the decision cannot be appealed.
                               <br>
                               <br>
                               C.<strong>Tax Court Opinion or Memorandum Opinion</strong> - The Chief Judge decides whether an opinion in a regular case will be issued as a Memorandum Opinion or as a Tax Court Opinion.
                               <br>
                               Generally, a Memorandum Opinion is issued in a regular case that does not involve a novel legal issue. A Memorandum Opinion addresses cases where the law is settled or factually driven. A Memorandum Opinion can be cited as legal authority, and the decision can be appealed. A Memorandum Opinion is cited as [<u>Name of Petitioner</u>] v. Commissioner, T.C. Memo. [year issued - #].
                              <br>
                              <br>
                               Generally, a Tax Court Opinion is issued in a regular case when the Tax Court believes it involves a sufficiently important legal issue or principle. A Tax Court Opinion can be cited as legal authority, and the decision can be appealed. A Tax Court Opinion is cited as [Name of Petitioner] v. Commissioner, [Volume of Tax Court Reports] T.C. [page of the volume] (year issued).

                             </ol>
                             <br>
                             The opinions of the Tax Court are posted daily on the Tax Court's website after 3:30 p.m. (Eastern time) under
                            <strong><a href="/todays-opinion" target="_blank" title="Today's Opinions">Today's Opinions</a></strong>
                             and categorized as described above. Bench Opinions issued after March 1, 2008, are electronically viewable on the Tax Court's website.""",
                "anchortag": "START2",
            },
            {
                "question": "Does a petitioner (taxpayer) ever win a case?",
                "answer": "Yes. Sometimes the petitioner wins some or all of the issues. Sometimes the IRS wins some or all of the issues. Sometimes, in a lien or levy case, the case may be sent back to the IRS to reconsider collection alternatives or other matters.",
                "anchortag": "START3",
            },
            {
                "question": "How will I find out whether I won or lost my case?",
                "answer": "You will receive a copy of the opinion by mail or a notification by electronic service. The Tax Court will also post the opinion on its website after 3:30 p.m. (Eastern time) on the day it is issued. Court personnel may call you to tell you the opinion is on the website. The opinion, written by the Judge, explains the conclusions reached after the trial or hearing. After the opinion is issued, a decision will be entered that is consistent with the opinion issued by the Judge.",
                "anchortag": "START4",
            },
            {
                "question": "What if I disagree with the opinion of the Judge?",
                "answer": "You may not appeal the Judge's decision in an S case. In a regular (non-S) case, you may appeal the Judge's decision or you may file a motion for reconsideration of an opinion within 30 days after the written opinion was mailed. Your motion for reconsideration should clearly explain what you disagree with and the reasons you believe your disagreement has merit. Normally, the Judge who decided your case will decide the motion for reconsideration. A motion for reconsideration will not usually be granted absent unusual circumstances or substantial error.",
                "anchortag": "START5",
            },
            {
                "question": "How do I file an appeal from the Judge’s decision? Can I appeal my case?",
                "answer": f"""If you chose, and the Tax Court granted you, small tax case status, there is no appeal from the decision of the Tax Court.
                <strong><a href="/petitioners_start#before12" target="_blank" title="">See the discussion above about choosing S case status</a></strong>
                . In an S case, neither the IRS nor the petitioner can appeal. The Judge's decision is final.
                            <br>
                            <br>
                            If your case is a regular case, you may appeal the decision to one of the U.S. Courts of Appeals. You must wait for a decision (as opposed to the opinion) to be entered by the Tax Court before you file an appeal. A decision is a judicial determination that disposes of a case. An opinion is a statement explaining the Tax Court's decision. The notice of appeal must be filed with the Tax Court within 90 days after the decision is entered, or 120 days if the IRS appeals first. The cost for filing a notice of appeal depends on the Federal Circuit Court to which the appeal is being made but generally costs $600-$605.
                            See <strong><a href="{petitioners_docs["Rule-190.pdf"]}" target="_blank" title="Rule 190">Tax Court Rules 190</a></strong>,
                            <strong><a href="{petitioners_docs["Rule-191.pdf"]}" target="_blank" title="Rule 191">191</a></strong>,
                            <strong><a href="{petitioners_docs["Rule-192.pdf"]}" target="_blank" title="Rule 192">192</a></strong>, and
                            <strong><a href="{petitioners_docs["Rule-193.pdf"]}" target="_blank" title="Rule 193">193</a></strong>.""",
                "anchortag": "START6",
            },
            {
                "question": "Will my documents be returned to me when the case is over?",
                "answer": 'Documents filed with the Court will not be returned to you. If you did not keep a copy of a document, you may request copies of particular documents by contacting the Court\'s Copywork Section by mail at: United States Tax Court, 400 Second Street, N.W., Washington, D.C. 20217-0002, or telephone at (202) 521-4688. There is a fee for copywork. See<strong><a href="/transcripts_and_copies" target="_blank" title="Transcripts & Copies">Transcripts & Copies</a></strong>. You may also view, download, or print any document filed in your case if you have registered for electronic access through <strong><a href="/dawson" target="_blank" title="DAWSON">DAWSON</a></strong>.',
                "anchortag": "START7",
            },
            {
                "question": "Do I need a transcript of the trial and how can I get a transcript?",
                "answer": 'A transcript of the trial is the typewritten record prepared by the reporting company reflecting everything that is said in court. A transcript is usually required if posttrial briefs are ordered by the Court and/or if your case is being appealed to the U.S. Court of Appeals. Each of the parties (petitioner and respondent) is responsible for ordering and paying for a copy of their own transcript. The reporting company is a private company and is not part of the Tax Court. You should talk with the reporter during the trial session or see <strong><a href="/transcripts_and_copies" target="_blank" title="Transcripts & Copies">Transcripts & Copies</a></strong> for more information. <br> <br>Transcripts are not viewable even to the parties through <strong><a href="/dawson" target="_blank" title="DAWSON">DAWSON</a></strong> until 90 days after the date of the trial (or hearing).',
                "anchortag": "START8",
            },
            {
                "question": "Are there any circumstances where the Court will pay for my transcript?",
                "answer": "In some very limited circumstances the Judge may direct that the Court pay for a transcript for a pro se petitioner. A pro se petitioner may file a motion requesting that the Court pay the expenses of a transcript. You must satisfy the Court that (1) you need a transcript to prepare posttrial briefs ordered by the Judge; (2) you do not have the financial means to pay for the transcript; and (3) the case presents a substantial question and is not frivolous. A Judge has discretion to grant or deny your motion. <br><br>You may be considered a pro se petitioner with respect to a motion requesting the Court pay the expenses of a transcript, if you represent yourself or if you are receiving assistance from a participating low-income taxpayer clinic or a participating bar-sponsored calendar call program.",
                "anchortag": "START9",
            },
            {
                "question": "Can I get money back from the IRS for my costs (but not taxes) if I win my case?",
                "answer": "There are some limited circumstances where a petitioner, as a prevailing party, can recover fees and costs from the IRS. In general, a party is not a prevailing party if the IRS establishes that its position was substantially justified. A request for fees and costs cannot be filed until after the parties have settled their dispute or the Tax Court has issued its opinion.",
                "anchortag": "START10",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Guidance for Petitioners - Things That Occur After Trial",
                body=[
                    {"type": "heading", "value": "Things That Occur After Trial"},
                    {"type": "questionanswers", "value": questions},
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
