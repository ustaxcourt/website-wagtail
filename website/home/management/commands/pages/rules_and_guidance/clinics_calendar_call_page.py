from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage, CommonText


docs = {
    "2021_calendar_call_program_sample_letter.pdf": "",
}


class ClinicsCalendarCallPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "clinics_calendar_call"
        title = "Clinics & Pro Bono Programs: Bar Sponsored Calendar Call Programs"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for document in docs.keys():
            uploaded_document = self.load_document_from_documents_dir(None, document)
            docs[document] = uploaded_document.file.url

        questions = [
            {
                "question": "Preamble",
                "answer": """
Many petitioners cannot afford to pay a practitioner to represent them. Rule 6.1(a) of the American Bar Association Model Rules of Professional Conduct, to which persons admitted to practice in the Court are subject, states that every lawyer should aspire to render at least 50 hours of pro bono legal services per year. The rule also states that a substantial majority of the 50 hours of service should be devoted to persons who are unable to pay for such services or to organizations assisting such persons.
<br/><br/>
Some Bar associations, integrated Bars, and other professional organizations administer Bar sponsored calendar call programs through which volunteer tax practitioners provide free legal assistance to self-represented petitioners. The United States Tax Court (the Court) recognizes the important assistance that calendar call programs provide to self-represented petitioners.
<br/><br/>
These programs assist petitioners in prosecuting a case in this Court. For calendar call programs which agree to abide by the requirements stated herein, the Court may announce at the start of a trial calendar that volunteer tax practitioners associated with the calendar call program are available to consult with and assist self-represented petitioners, and the Court may introduce the volunteers who are present in the courtroom. In addition, in 25 cities in which the Tax Court holds trial sessions, petitioners' counsel room is reserved for persons admitted to practice before the Court, including attorneys associated with tax clinics and Bar sponsored calendar call programs. The Tax Court does not endorse or recommend any particular clinic or Bar sponsored calendar call program.
<br/><br/>
The Court will apply the following requirements with regard to participation by Bar sponsored calendar call programs in proceedings before the Court.
                """,
                "anchortag": "PREAMBLE",
            },
            {
                "question": "Sec. 1. General Requirements for Participation by Calendar Call Programs",
                "answer": f"""To participate a Bar sponsored calendar call program shall:
<ol type="a">
<li>
Constitute a program organized by a Bar association, integrated Bar, or similar professional organization in which volunteer tax practitioners provide pro bono consultation services to self-represented petitioners at Tax Court calendar calls. Each such program shall have a program director/coordinator who shall be responsible for overseeing program operations and serve as a point of contact for communications to and from the Court.
</li>
<li>
Establish guidelines for assisting self-represented petitioners, including therein the objectives of public service and judicial and administrative economy.
</li>
<li>
Submit to the Chief Judge, on or before February 15 of each year, a letter, signed by the program director/coordinator (<a href="{docs['2021_calendar_call_program_sample_letter.pdf']}" title="Suggested Form Letter to Chief Judge">sample</a> format attached), which includes (1) the name, address, Tax Court Bar number (if applicable), and contact information (including the e-mail address) of the calendar call program director/coordinator; (2) the place(s) of trial served by the program; (3) whether the program provides assistance to self-represented petitioners in small tax cases, regular tax cases, or both; (4) a statement that the program will comply with these requirements; (5) a copy of or electronic link to the program guidelines as described in section 1.b., above; (6) an approximate number of petitioners for whom the calendar call program provided consultation, assistance and/or advice at the trial session during the calendar year preceding the submission of the letter; and (7) any suggestions that the program may offer for better assisting self-represented petitioners in their interactions with the Court. The letter to the Chief Judge referred to in this provision may be submitted to the Court in paper form or, if in PDF format, as an attachment to an e-mail using the <a href="mailto:litc@ustaxcourt.gov" title="Email: litc@ustaxcourt.gov">Contact Us</a> link.
</li>
<li>
Immediately inform the Chief Judge of any material changes in the information submitted to the Court pursuant to section 1.c., above.
</li>
</ol>
""",
                "anchortag": "SEC1",
            },
            {
                "question": "Sec. 2. Specific Requirements for Participation by Bar Sponsored Calendar Call Programs",
                "answer": """Volunteer practitioners participating in calendar call programs described in these requirements may participate in calendar call proceedings under the following circumstances:
                <ol type="a">
                <li>
                Each practitioner participating in a calendar call program shall be a member in good standing of the Bar of the Court.
                </li>
                <li>
                Each practitioner participating in a calendar call program shall arrive at the Court at least one hour before the beginning of a calendar call and inform the trial clerk of his or her availability to assist self-represented petitioners.
                </li>
                <li>
                A practitioner participating in a calendar call program shall not directly or indirectly suggest that a petitioner may retain the practitioner’s services for a fee, nor may the practitioner receive a fee from the petitioner.
                </li>
                <li>
                Practitioners participating in a calendar call program may engage in any activity necessary and appropriate to assist petitioners, consistent with all applicable codes of professional conduct, including, but not limited to: (1) providing procedural advice to petitioners who decide to proceed to trial, (2) consulting with petitioners regarding the merits of their cases and evaluating any settlement proposals from the Internal Revenue Service, (3) acting as a communicator or mediator between the parties in an effort to assist in resolving the case, and/or (4) entering an appearance with the Court on the petitioner’s behalf.
                </li>
                <li>
                Any practitioner participating in a calendar call program who has not (1) entered an appearance with the Court on the petitioner’s behalf, or (2) received a power of attorney from the petitioner authorizing the practitioner to represent the petitioner, shall conduct all case-related discussions with Internal Revenue Service attorneys in the presence of the petitioner and with the petitioner’s permission in order to alleviate any concerns regarding disclosure of petitioner information.
                </li>
                </ol>
                """,
                "anchortag": "SEC2",
            },
            {
                "question": "Sec. 3. Calendar Call Announcement",
                "answer": """If these requirements are satisfied and the Court permits a calendar call program to participate, the Court may announce at the beginning of a calendar call that volunteer practitioners participating in the calendar call program are available to consult with and assist self-represented petitioners and the Court may introduce the volunteer practitioners who are present in the courtroom.""",
                "anchortag": "SEC3",
            },
            {
                "question": "Sec. 4. Termination of Participation",
                "answer": """The Court, in its discretion, may terminate participation by a calendar call program at any time, provided notice stating the cause for the termination is furnished to the calendar call program director/coordinator.""",
                "anchortag": "SEC4",
            },
            {
                "question": "Reference Documents",
                "answer": f"""<ul>
                    <li><a href="{docs['2021_calendar_call_program_sample_letter.pdf']}" title="Sample Letter">Letter to Chief Judge (sample): 2021_calendar_call_program_sample_letter.pdf</a><br/></li>
                    </ul>
                """,
                "anchortag": "REFDOCS",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description=title,
                show_in_menus=False,
                body=[
                    {
                        "type": "h2",
                        "value": "Requirements For Participation in the United States Tax Court Clinical, Student Practice & Calendar Call Program by Bar Sponsored Calendar Call Programs",
                    },
                    {"type": "questionanswers", "value": questions},
                    {
                        "type": "snippet",
                        "value": CommonText.objects.get(
                            name="Clinics Contact Details"
                        ).id,
                    },
                ],
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Successfully created the '{title}' page.")
