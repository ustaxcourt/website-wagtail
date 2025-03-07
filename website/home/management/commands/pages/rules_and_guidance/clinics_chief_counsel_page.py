from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    EnhancedStandardPage,
)


docs = {
    "2021_letter_to_CJ_academic_law_and_nonlaw.pdf": "",
    "clinics_counsel_rooms.pdf": "",
    "stuffer_notice.pdf": "",
}


class ClinicsChiefCounselPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "clinics_chief_counsel"
        title = "Clinics & Pro Bono Programs: Office of Chief Counsel Student Practice Program"

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
The Office of Chief Counsel, Internal Revenue Service, offers a program for law student volunteers, paid law student interns, and law student summer interns (student practice program). The United States Tax Court (the Court) recognizes the benefits that the student practice program provides to both law students and the Office of Chief Counsel. In appropriate circumstances, the Court permits law students enrolled in this program to participate in Court hearings and trials.
<br/><br/>
The Court will apply the requirements set forth below with regard to participation by the Chief Counsel Student Practice Program.
                """,
                "anchortag": "PREAMBLE",
            },
            {
                "question": "Sec. 1. Requirements for Participation by Office of Chief Counsel Student Practice Program",
                "answer": """To participate in the Court’s student practice program, the student shall:
<ol type="a">
<li>
Be supervised and directed by a Chief Counsel attorney (the director) who is a member in good standing of the Bar of the Court and who shall serve as a point of contact for communications to and from the Court.
</li>
<li>
Establish guidelines for screening cases that are appropriate for the student practice program. Those guidelines shall include the objectives of public service, educational experience, and judicial and administrative economy.
</li>
<li>
Inform all persons associated with the student practice program that the Chief Counsel trial attorney assigned to the case (lead counsel), who shall be a member in good standing of the Bar of the Court, is personally responsible at all times to the Court for meeting deadlines, monitoring case preparation, ensuring full compliance with the Court’s Rules of Practice and Procedure and with orders issued by the Court, and in general, with properly preparing a case for hearing, trial, or other disposition.
</li>
<li>
Submit to the Chief Judge, on or before February 15 of each year, a letter which includes (1) the name, address, and contact information (including the e-mail address) of the student practice program director (sample format attached); (2) a statement that the student practice program will comply with these requirements; (3) a general description of the student practice program guidelines as described in section 1.b., above; and (4) any suggestions that the student practice program may offer for enhancing student interactions with the Court. The letter to the Chief Judge referred to in this provision may be submitted to the Court in paper form or, if in PDF format, as an attachment to an e-mail using the Contact Us link.
</li>
<li>
Immediately inform the Chief Judge of any material changes in the information submitted to the Court pursuant to section 1.d., above.
</li>
</ol>
""",
                "anchortag": "SEC1",
            },
            {
                "question": "Sec. 2. Appearance and Representation",
                "answer": """
                A responsive pleading, motion, or other paper may be filed with the Court through the student practice program under the following circumstances:
                <ol type="a">
                <li>
Any responsive pleading, motion, or other paper filed with the Court shall be reviewed by lead counsel and lead counsel’s signature shall appear first on the document. The names of other counsel who are members in good standing of the Bar of this Court also may appear on the document. A student may not sign a document submitted to the Court for filing. However, the names of students may appear in the answer or other documents filed in the case to the extent provided in section 3.c. below.
                </li>
                <li>
Contacts made on behalf of the Commissioner of Internal Revenue with the Court concerning a case described in these requirements generally should be made only by the director of the student practice program or lead counsel. A student participant may not contact the Court concerning a case described in these requirements.
                </li>
                </ol>
                """,
                "anchortag": "SEC2",
            },
            {
                "question": "Sec. 3. Student Participation in Court Proceedings",
                "answer": """
If the requirements set forth above are satisfied, the Court may permit students in the student practice program to participate in proceedings before the Court pursuant to the following procedures:

<ol type="a">
<li>
When a case described in these requirements is called for hearing or trial, lead counsel shall answer the calendar call, advise the Court whether the case is ready for hearing or trial, and introduce any student in the student practice program who requests permission to participate in that case.
</li>
<li>
If the Court permits a student to participate in a case upon compliance with subsection (a), lead counsel shall remain in the courtroom and sit at respondent’s counsel table at all times during the hearing or trial of the case. A student who is permitted to participate in a case may, in the discretion of the presiding Judge or Special Trial Judge, present all or any part of a case at a hearing or trial. However, the presiding Judge or Special Trial Judge shall at all times retain the discretion to require the student participant to step aside and to require the lead counsel to complete the hearing or trial.
</li>
<li>
A student practice program submitting a pleading, motion, stipulation, or other paper to the Court for filing may include a statement in the body of the document including the name of any student enrolled in the program who participated in preparation of the document. However, a student may not sign a document submitted to the Court for filing.
</li>
</ol>
                """,
                "anchortag": "SEC3",
            },
            {
                "question": "Sec. 4. Termination of Participation",
                "answer": """The Court, in its discretion, may terminate participation by the student practice program at any time, provided notice stating the cause for the termination is furnished to the Office of Chief Counsel.""",
                "anchortag": "SEC4",
            },
            {
                "question": "Reference Documents",
                "answer": f"""<ul>
                    <li><a href="{docs['2021_letter_to_CJ_academic_law_and_nonlaw.pdf']}" title="Sample Letter">Letter to Chief Judge (Sample): 2021_letter_to_CJ_academic_law_and_nonlaw.pdf</a><br/></li>
                    <li><a href="{docs['stuffer_notice.pdf']}" title="Format for Stuffer Notice">Format for Stuffer Notice: stuffer_notice.pdf</a></li>
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
                        "type": "paragraph",
                        "value": """Please <a href="mailto:litc@ustaxcourt.gov" title="email: litc@ustaxcourt.gov">contact us</a> with any questions concerning the Court’s program or requirements, or call <a href="tel:202-521-3366" title="call: 202-521-3366">202-521-3366</a>.""",
                    },
                ],
            )
        )

        new_page.save_revision().publish()
        self.logger.write(f"Successfully created the '{title}' page.")
