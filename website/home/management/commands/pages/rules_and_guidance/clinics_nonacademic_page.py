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


class ClinicsNonAcademicPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "clinics_nonacademic"
        title = "Clinics & Pro Bono Programs: Nonacademic Clinical Programs"

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
Many nonacademic tax clinics and attorney referral programs (nonacademic clinics) provide free legal assistance to low income and self-represented petitioners. The two most common nonacademic clinic models are: (1) Clinics that assign cases to practitioners who are employees of the clinic, and (2) clinics that have a relationship with outside practitioners who have agreed to provide pro bono legal services and also participate in a calendar call program.
<br/>
<br/>
Nonacademic clinics help self-represented petitioners comply with the Internal Revenue Code and to deal appropriately with the Internal Revenue Service and the Federal courts. The United States Tax Court (the Court) recognizes the important assistance that nonacademic clinics provide to self-represented petitioners.
<br/>
<br/>
For nonacademic clinics which agree to abide by the requirements stated herein, the Court includes standard information about the clinic in mailings to petitioners and permits students/fellows to participate in Court hearings and trials. In addition, in 25 cities in which the Tax Court holds trial sessions, petitioners' counsel room is reserved for persons admitted to practice before the Court, including attorneys associated with tax clinics and Bar sponsored calendar call programs. The Tax Court does not endorse or recommend any particular clinic or Bar sponsored calendar call program.
<br/>
<br/>
The Court applies the following requirements with regard to participation in the Court’s nonacademic clinic program.
""",
                "anchortag": "PREAMBLE",
            },
            {
                "question": "Sec. 1. Requirements for Participation by Nonacademic Clinics",
                "answer": f"""A nonacademic clinic participating in the Court’s nonacademic clinical program shall not charge any fee for legal services to petitioners. An nonacademic clinic may ask petitioners using its services to reimburse the clinic for incidental costs such as filing fees, copying costs, and postage charges. To participate in the Court’s nonacademic clinical program, a nonacademic clinic shall:
<ol type="a">
<li>
Designate a clinic director/coordinator who shall be responsible for overseeing program operations and serve as a point of contact for communications to and from the Court.
</li>
<li>
Restrict its assignment or referral of Tax Court cases to practitioners who are members in good standing of the Bar of the Court.
</li>
<li>
Be operated by an exempt organization as described in I.R.C. sec. 501(c)(3) and exempt from tax under I.R.C. sec. 501(a).
</li>
<li>
Establish guidelines for screening cases, including therein the objectives of public service and judicial and administrative economy. These guidelines should be interpreted so that assistance is offered, as appropriate, to low income petitioners who have filed a petition with the Court or who expect to do so.
</li>
<li>
Establish guidelines and procedures for case progress reporting to the nonacademic clinic director/coordinator by practitioners accepting assignments or referrals of Tax Court cases. Nonacademic clinics also shall require all practitioners and clients to sign a Representation Agreement which clearly states the terms and limitations of the representation.
</li>
<li>
Comply with the U.S. Tax Court Requirements for Academic Clinical Programs if the nonacademic clinic is associated with a clinic operated by an accredited law school.
</li>
<li>
Submit to the Chief Judge, on or before February 15 of each year, a letter signed by the clinic director/coordinator (<a href="{docs['2021_letter_to_CJ_academic_law_and_nonlaw.pdf']}" title="Sample Letter" >sample</a> format attached) which includes (1) the name, address, Tax Court Bar number (if applicable) and contact information (including the e-mail address) of the nonacademic clinic director/coordinator. If the nonacademic clinic director/coordinator does not have a Tax Court Bar number, the name, address and Tax Court Bar number of a practitioner associated with the clinic who is admitted to the Court should also be listed; (2) the place(s) of trial served by the nonacademic clinic; (3) a statement that the nonacademic clinic will comply with these requirements and that the nonacademic clinic is operated by an exempt organization as described in I.R.C. sec. 501(c)(3) and exempt from tax under I.R.C. sec. 501(a); (4) a copy of or electronic link to the nonacademic clinic’s guidelines as described in sections 1.d. and 1.e., above; (5)(a) during the calendar year preceding submission of the letter, an approximate number of petitioners with cases pending in the Court for whom the nonacademic clinic entered an appearance pursuant to Tax Court Rule 24; (b) an approximate number of petitioners who were represented (e.g., through a Power of Attorney) but for whom the nonacademic clinic did not enter an appearance; and (c) an approximate number of petitioners for whom the nonacademic clinic provided consultation, assistance and/or advice (e.g., at the Calendar Call), but did not represent the taxpayer; (6) whether the nonacademic clinic has a relationship with outside attorneys for referral of cases or operation of a calendar call program; (7) any suggestions that the nonacademic clinic may offer for better assisting low income petitioners in their interactions with the Court; (8) an updated one page stuffer notice that the Court can use to notify petitioners of the availability of the nonacademic clinic’s services for the coming year (<a href="{docs['stuffer_notice.pdf']}" title="Format for Stuffer Notice" >format for stuffer notice</a> attached); and (9) whether the nonacademic clinic would like its stuffer notice to be sent to petitioners in regular tax cases, small tax cases, or both; A version of the stuffer notice written in Spanish may be submitted on the reverse side of the English version. Information about clinics that do not offer assistance in Spanish should not be included in a Spanish language stuffer notice. The Spanish version should include a translation of the following sentence: <strong>"Please be advised that all proceedings in the Tax Court are in English."</strong> The letter to the Chief Judge and updated stuffer notice referred to in this provision may be submitted to the Court in paper form or, if in PDF format, as an attachment to an e-mail using the <a href="mailto:litc@ustaxcourt.gov" title="Email litc@ustaxcourt.gov">Contact Us</a> link.
</li>
<li>
If the nonacademic clinic participates in, or coordinates a calendar call program, the provisions of Section 2 of the Court’s Requirements for Bar Sponsored Calendar Call Programs apply.
</li>
<li>
Immediately inform the Chief Judge of any material changes in the information submitted to the Court pursuant to section 1.g., above.
</li>
</ol>
""",
                "anchortag": "SEC1",
            },
            {
                "question": "Sec. 2. Responsibilities of Counsel",
                "answer": """A practitioner accepting an assignment or referral of a Tax Court case from a nonacademic clinic shall satisfy the following requirements:
                <ol type="a">
                <li>Be a member in good standing of the Bar of the Court and adhere to the Court’s Rules of Practice and Procedure.</li>
                <li>Assume personal responsibility for meeting deadlines, monitoring case preparation, ensuring full compliance with the orders issued by the Court, and, in general, properly preparing a referred case for hearing, trial, or other disposition.</li>
                <li>A practitioner who is not employed by a nonacademic tax clinic and who accepts a case referral from a nonacademic clinic generally shall not accept any fee or payment as compensation for professional services rendered in that case. However, a nonacademic clinic may compensate a practitioner by paying a stipend and/or reimbursing the practitioner for actual costs (e.g., the $60.00 Court filing fee and costs of copying and transcripts).</li>
                </ol>
                """,
                "anchortag": "SEC2",
            },
            {
                "question": "Sec. 3. Appearance and Representation",
                "answer": """
<ol type="a">
<li>A practitioner who is employed by a nonacademic clinic or who accepts a case referral from a nonacademic clinic shall be lead counsel in the case, and the name, Bar number, and signature of that practitioner shall appear first on any petition filed with the Court. The names, Bar numbers, and signatures of other practitioners who are admitted to practice before the Court may also appear on the petition below the name of the lead counsel. A student may not sign a document submitted to the Court for filing. However, the names of students may appear in the petition or other documents filed in the case to the extent provided in section 4.d. below.
</li>
<li>
If a petition has been filed with the Court, and the petitioner is not represented by counsel, a practitioner who is employed by a nonacademic clinic or a practitioner who accepts a case referral from a nonacademic clinic shall sign and file an entry of appearance with the Court pursuant to Rule 24(a)(3), Tax Court Rules of Practice and Procedure, and he or she shall be designated lead counsel in the case. Any other practitioner who is a member of the Bar of the Court who intends to appear as counsel in the case shall likewise file an entry of appearance.
</li>
<li>
If a practitioner who is employed by a nonacademic clinic or who accepts a case referral from a nonacademic clinic finds it necessary or appropriate to withdraw from a case or effectuate a substitution of counsel, he or she must comply with the requirements of Rule 24(c) and (d), Tax Court Rules of Practice and Procedure.
</li>
</ol>
""",
                "anchortag": "SEC3",
            },
            {
                "question": "Sec. 4. Student/Fellow Participation in Court Proceedings",
                "answer": """If the requirements set forth above are satisfied, the Court will permit students who are enrolled and in good standing with a law school accredited by the American Bar Association, and law school graduates serving as fellows associated with a nonacademic clinic, to participate in proceedings before the Court pursuant to the following procedures:
                <ol type="a">
                <li>
                Lead counsel that intends to request permission for a student/fellow to participate in proceedings before the Court shall obtain from the petitioner advance written consent for the student/fellow to participate in the case. Although lead counsel should retain a copy of the written consent in each case file, there is no need to submit the consent to the Court.
                </li>
                <li>
                When a case described in these requirements is called for hearing or trial, lead counsel shall answer the calendar call, advise the Court whether the case is ready for hearing or trial, and introduce any student/fellow who seeks permission to participate in the proceedings.
                </li>
                <li>
                If the Court permits a student/fellow to participate in a case upon compliance with subsections (a) and (b), lead counsel shall remain in the courtroom at petitioner’s counsel table at all times during the hearing or trial of the case. A student/fellow who is permitted to participate in a case may, at the discretion of the presiding Judge or Special Trial Judge, present all or any part of a petitioner’s case at a hearing or trial. However, the presiding Judge or Special Trial Judge may at any time exercise the discretion to require the student/fellow to step aside and to require lead counsel to complete the hearing or trial.
                </li>
                <li>
                A nonacademic clinic submitting a pleading, motion, stipulation, or other paper to the Court for filing may include a statement in the body of the document including the name of any student/fellow assisting the nonacademic clinic who participated in preparation of the document. However, a student/fellow may not sign a document submitted to the Court for filing.
                </li>
                </ol>
                """,
                "anchortag": "SEC4",
            },
            {
                "question": "Sec. 5. Nonacademic Clinic Contact Information",
                "answer": """If these requirements are satisfied and the Court permits a nonacademic clinic to participate in this program, the Court will use stuffer notices to provide petitioners with contact information for the nonacademic clinic. It is important that the nonacademic clinic immediately inform the Court of any change in director, address or telephone number.""",
                "anchortag": "SEC5",
            },
            {
                "question": "Sec. 6. Termination of Participation",
                "answer": """The Court, in its discretion, may terminate participation in the program by an academic clinic at any time, provided notice stating the cause for the termination is furnished to the academic clinic director. In such a case, counsel of record would be required to file a motion to withdraw, pursuant to Rule 24(c), Tax Court Rules of Practice and Procedure.""",
                "anchortag": "SEC6",
            },
            {
                "question": "Reference Documents",
                "answer": f"""<ul>
                    <li><a href="{docs['2021_letter_to_CJ_academic_law_and_nonlaw.pdf']}" title="Sample Letter">Letter to Chief Judge (sample): 2021_letter_to_CJ_academic_law_and_nonlaw.pdf</a><br/></li>
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
                        "value": "Requirements For Participation in the United States Tax Court Clinical, Student Practice & Calendar Call Program by Nonacademic Clinics",
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
