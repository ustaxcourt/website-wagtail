from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage


class PetitionersDuringPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners-during"
        title = "Guidance for Petitioners: Things That Occur During Trial"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        questions = [
            {
                "question": "What happens at the beginning of the trial session?",
                "answer": "On the first morning of the trial session, a Tax Court employee, the trial clerk, will announce the name of (call) each case that has not been settled. This process is known as a calendar call. Be sure to arrive in court in time to attend the calendar call. When your name is called by the trial clerk, come forward and identify yourself to the Judge by stating your name. The attorney representing the IRS will also state his/her name. The Judge may ask a few questions to determine the status of your case.<br/><br/>In many cities, there are tax clinics and organizations of tax practitioners that we refer to as calendar call programs; these practitioners may provide assistance to unrepresented taxpayers. If there is such a clinic or calendar call program in the city where you have requested trial, the Judge may identify the volunteer practitioners at the beginning of the trial session. If you want to speak with one of the clinic or calendar call lawyers, you should ask the Judge for an opportunity to do so.<br/><br/>After the calendar call, the Judge will schedule cases for trial at specific times and days during the trial session. The time and date for your trial will be announced by the Judge or the trial clerk.<br/><br/>Beginning two weeks before the start of a trial session, the parties may also jointly contact a Judge's chambers to request a time and date certain for trial. The Judge will attempt to accommodate the request, if practicable. You may not need to appear at the calendar call if your case has been set for a time and date certain.",
                "anchortag": "DURING1",
            },
            {
                "question": "What if I can't come to Court on the date set for trial or I am not ready for trial?",
                "answer": 'There may be a few options:<br/><br/><ol class="arabic-numbers"><li>As early as possible, you may ask the Judge to postpone your trial by filing a motion for continuance. Depending on the circumstances, the Judge may or may not grant that request.</li><li>You should ask the IRS attorney if he or she will agree with the request for continuance and you should let the Tax Court know if there is any objection. The Judge may or may not grant your request for continuance. If your request is not granted, you must be prepared to try your case.</li><li>Sometimes a case can be considered by the Tax Court without the need for testimony or a trial. If you and the IRS agree about all of the facts and documents you want admitted into the record, talk with the IRS attorney about whether your case can be submitted without a trial (fully stipulated). To do this, you and the IRS attorney must include in a stipulation all of the agreed facts and documents necessary for the Tax Court to reach its decision. The Judge will review the stipulation and make a decision based solely on the documents and facts agreed to by you and the IRS attorney. If your case can be submitted fully stipulated to the Tax Court in advance of the date set for the calendar call, you will not need to come to court.</li></ol>\n',
                "anchortag": "DURING2",
            },
            {
                "question": "What happens if I don't show up for Court?",
                "answer": "If you do not come to court for the calendar call or at the date and time set for trial and you have not been otherwise excused by the Tax Court, your case may be dismissed for failure to prosecute and a decision may be entered against you. If your case is dismissed for failure to prosecute, it means you lose your case.<br/><br/>Be sure that you contact the Tax Court and the IRS as soon as possible if you can't come to court at the scheduled time and date.",
                "anchortag": "DURING3",
            },
            {
                "question": "If my spouse and I have filed a joint petition with the Tax Court, do we both need to come to court on the date set forth in the notice of trial?",
                "answer": "Yes. Both parties' signatures may be needed for important papers such as a stipulation of facts, a stipulation of settled issues, or a stipulated decision. If either party fails to attend the trial, that party forfeits the opportunity to testify or present any other evidence. The Judge may decide to enter a decision for a spouse who is absent on the same basis as is entered for the spouse who attended the trial. Under some circumstances, upon advance request, the Judge may excuse one of the spouses from appearing at trial.",
                "anchortag": "DURING4",
            },
            {
                "question": "Who represents the IRS?",
                "answer": "An attorney who works for the Office of Chief Counsel of the IRS will represent the IRS in each case.",
                "anchortag": "DURING5",
            },
            {
                "question": "What if I have difficulty speaking and understanding English?",
                "answer": 'It is generally the responsibility of each petitioner to bring someone to court who can help in communicating in English with the Judge and the IRS attorney. In some cities, the Tax Court may have an interpreter available to help the Judge on the first day of the trial session. You should let the Judge and the IRS know as early as possible that you will require help with English. Sometimes the IRS will also have someone who can help.<br/><br/>See the related questions and answers in the "<strong><a href="/petitioners-start#START6" title="Starting A Case">Starting a Case</a></strong>" section.',
                "anchortag": "DURING6",
            },
            {
                "question": "Someone told me that the petitioner (taxpayer) has the burden of proof. I don't understand this. What is the burden of proof?",
                "answer": "The burden of proof is a legal term that refers to a party's duty to prove a disputed assertion. The burden of proof is generally on the petitioner. This means that you need to bring to court evidence, such as documents and testimony of witnesses (you and maybe others), to prove that the determination of the IRS is not correct and that your position is correct.<br/><br/>There are some limited circumstances where the burden of proof is on the IRS. For the burden of proof to shift to the IRS on a factual issue, the petitioner must introduce credible evidence in court with respect to that issue. The petitioner must also comply with substantiation and record-keeping requirements set forth in the tax laws. Also the petitioner must show that he or she cooperated with reasonable requests from the IRS for witnesses, information, documents, meetings, and interviews. In most cases, the burden of proof does not shift to the IRS and the petitioner must show that the IRS's determinations are wrong.",
                "anchortag": "DURING7",
            },
            {
                "question": "What happens at the trial?",
                "answer": 'The trial clerk will call your case, and both you and the IRS attorney will state your names. For proceedings specific to COVID-19, refer to the Tax Court\'s <strong><a href="/covid" title="COVID-19 Resources">COVID-19 Resources</a></strong> page and information on <strong><a href="/zoomgov" title="Zoomgov Proceedings">Zoomgov</a></strong> proceedings.<br/><br/>The Judge may ask a few questions and dispose of other preliminary matters such as the filing of the stipulation of facts and pretrial memoranda. The Judge may allow each party to make an opening statement. An opening statement is simply a statement of what that party believes the facts and law are and how the Judge should rule. The petitioner usually goes first.<br/><br/>Caution: Opening statements generally are not made under oath, and facts alleged in opening statements cannot be considered by the Judge unless they are established by other evidence such as sworn testimony. Sometimes the petitioner makes an opening statement under oath to avoid the need for repeating the same facts later during the trial.<br/><br/>After the opening statements have been made, you may present your first witness. The purpose of a witness is to present information to the Judge that is relevant and from which the Judge can find facts. Often, the first, and sometimes the only, witness is you. You will take an oath or affirm to tell the truth and then tell your side of the case. If you are not representing yourself, your representative will ask you questions. This is called direct examination.<br/><br/>When you have concluded your testimony, the IRS attorney will have an opportunity to ask you questions. This is called cross-examination. After cross-examination you can ask the Judge for an opportunity to clarify any answers you provided with additional testimony. If you have witnesses other than yourself, the same procedure will be followed.<br/><br/>After you have concluded your side of the case, the IRS attorney can call witnesses and ask questions (direct examination).<br/><br/>After direct examination of each witness by the IRS, you can ask the witness questions (cross-examination). Throughout the trial, the Judge may ask questions and request clarification of evidence from both sides.<br/>After all the witnesses have testified and all the documents have been entered into evidence, the trial will be over and the record will be closed. This means that no more evidence may be submitted to the Court.<br/><br/>Reminder: The Judge can consider only evidence admitted into the record of your case. Therefore, you should bring with you to court all of your documents not already included in a stipulation of facts even if you provided them to the IRS earlier. <br/><br/><strong>Some Dos and Don\'ts of Trial<br/></strong><br/><ul class="disc"><li>Do organize all your papers and documents and bring them with you.</li><li>Do present your facts and state your position to the Judge.</li><li>Do respect the Judge and the Tax Court.</li><li>Don\'t bring food or chew gum in court.</li><li>Do turn off cell phones and other electronic devices in the courtroom.</li><li>Don\'t argue with a witness, but do ask questions.</li><li>Don\'t argue with the IRS attorney, but do state your position to the Judge.</li></ul>',
                "anchortag": "DURING8",
            },
            {
                "question": "Does a case ever get settled after trial?",
                "answer": "Yes. Sometimes during or after trial, one of the parties or the Judge will suggest that the parties talk to each other with the goal of settling the case. On occasion the petitioner's and/or the IRS attorney's evaluation of the merits of the case may change after trial. Such circumstances may provide an opportunity for settlement discussions.",
                "anchortag": "DURING9",
            },
            {
                "question": "Is there a stenographer or a recording of the trial?",
                "answer": 'Yes. The Tax Court is a court of record. This means that everything that happens in court will be recorded. The Tax Court contracts with an independent reporting company who records the entire trial. Because the reporter recording the trial is not a Tax Court employee, you should not leave any documents with the reporter. You can obtain more information about the typewritten record of the trial (<strong><a href="/petitioners-after#AFTER7">Transcript</a></strong>) under the section "<strong><a href="/petitioners-after" title="After Trial">After Trial</a></strong>".',
                "anchortag": "DURING10",
            },
        ]
        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description=title,
                body=[
                    {"type": "h2", "value": "Things That Occur During Trial"},
                    {"type": "questionanswers", "value": questions},
                ],
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
