from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import (
    EnhancedStandardPage,
)


docs = {
    "2021_letter_to_CJ_academic_law_and_nonlaw.pdf": "",
    "stuffer_notice.pdf": "",
}


class ClinicsAcademicNonLawSchoolPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "clinics_academic_non_law_school"
        title = (
            "Clinics & Pro Bono Programs: Academic Clinical Programs (Non Law School)"
        )

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
                "answer": """Accredited colleges and universities operate academic tax clinics (academic clinics) that provide free assistance to low income and self-represented petitioners. Some academic clinics are supervised by practitioners who are admitted to practice before the Court while other clinics may provide a referral to outside attorneys who provide free legal assistance to low income petitioners or who operate a calendar call program.
                <br />
                Academic clinics help self-represented petitioners to comply with the Internal Revenue Code and to deal appropriately with the Internal Revenue Service and the Federal courts. The United States Tax Court (the Court) acknowledges the important assistance that academic clinics provide to self-represented petitioners.
                <br />
                For academic clinics operated by a college or university which agree to abide by the requirements stated herein, the Court includes information about the clinic in mailings to self-represented petitioners. In addition, in 25 cities in which the Tax Court holds trial sessions, petitioners’ counsel room is reserved for persons admitted to practice before the Court, including attorneys associated with tax clinics and Bar sponsored calendar call programs. The Tax Court does not endorse or recommend any particular clinic or Bar sponsored calendar call program.
                <br />
                The Court applies the following requirements with regard to academic clinics operated by a college or university.""",
                "anchortag": "PREAMBLE",
            },
            {
                "question": "Sec. 1. Requirements for Participation by Academic Clinics (Non Law School)",
                "answer": f"""An academic clinic operated by a college or university participating in the Court’s academic clinical program shall not charge any fee for services to taxpayers. An academic clinic may ask taxpayers using its services to reimburse the clinic for incidental costs such as filing fees, copying costs, and postage charges. To participate in the Court’s academic clinical program, an academic clinic shall:
<ol type="a">
<li>Constitute a clinical program offered by an accredited college or university in which a student receives academic credit(s). An academic clinic shall be supervised by a director who shall serve as a point of contact for communications to and from the Court. If the director is an adjunct member of the faculty or part-time member of the staff of the sponsoring college or university, the signature of an administrative official employed by the institution is required on the letter to the Chief Judge (see sec. 1.e.).</li>
<li>Establish guidelines for screening cases, including therein the objectives of public service and judicial and administrative economy. An academic clinic’s guidelines should be interpreted so that assistance is offered, as appropriate, to low income petitioners who have filed a petition with the Court or who expect to do so.</li>
<li>Either have on staff at least one practitioner (clinic practitioner) who is a member in good standing of the Bar of the Court or establish guidelines and procedures for case progress reporting to the clinic director by practitioners accepting assignments or referrals of Tax Court cases. If the academic clinic has a clinic practitioner on staff, all persons associated with the academic clinic shall be informed that the clinic practitioner is personally responsible at all times to the Court and to the taxpayer/petitioner for meeting deadlines, monitoring case preparation, ensuring full compliance with the Court’s Rules of Practice and Procedure and with orders issued by the Court, and, in general, properly preparing a case for hearing, trial, or other disposition. Although the Court recommends that academic clinics provide written notice to petitioners under this provision, and retain a copy of such notice in each case file, there is no need to submit a copy of any such notice to the Court.</li>
<li>Comply with the U.S. Tax Court Requirements for Nonacademic Clinical Programs if the academic clinic is associated with a nonacademic clinic.</li>
<li>Submit to the Chief Judge, on or before February 15 of each year, a letter signed by the clinic director (<a href="{docs["2021_letter_to_CJ_academic_law_and_nonlaw.pdf"]}" title="sample letter">sample</a> format attached) and/or an administrative official of the college or university (see sec. 1.a.) which includes: (1) the name, address, Tax Court Bar number (if applicable) and contact information (including the e-mail address) of the clinic director and all clinic practitioners; (2) the place(s) of trial served by the clinic; (3) a statement that the academic clinic will comply with these Requirements; (4) a copy of or electronic link to the academic clinic’s guidelines as described in section 1.b., above; (5) whether students are enrolled or otherwise participating in the clinical program spring/summer/fall semester(s), or year round; (6)(a) during the calendar year preceding submission of the letter, an approximate number of petitioners with cases pending in the Court for whom the academic clinic entered an appearance pursuant to Tax Court Rule 24; (b) an approximate number of petitioners who were represented (e.g., through a Power of Attorney) but for whom the academic clinic did not enter an appearance; and (c) an approximate number of petitioners for whom the academic clinic provided consultation, assistance and/or advice (e.g., at the Calendar Call), but did not represent the taxpayer; (7) whether the academic clinic has a relationship with outside attorneys for referral of cases or operation of a calendar call program; (8) any suggestions that the academic clinic may offer for better assisting low income petitioners in their interactions with the Court; (9) an updated one page stuffer notice that the Court can use to notify petitioners of the availability of clinic services for the coming year (<a>format for stuffer notice</a> attached); (10) whether the academic clinic would like its stuffer notice to be sent to petitioners in regular tax cases, small tax cases, or both; and (11) the name of the organization granting accreditation to the educational institution. A version of the stuffer notice written in Spanish may be submitted on the reverse side of the English version. Information about clinics that do not offer assistance in Spanish should not be included in a Spanish language stuffer notice. The Spanish version should include a translation of the following sentence: "Please be advised that all proceedings in the Tax Court are in English." The letter to the Chief Judge and updated stuffer notice referred to in this provision may be submitted to the Court in paper form or, if in PDF format, as an attachment to an e-mail using the Contact Us link.</li>
<li>If the academic clinic participates in, or coordinates a calendar call program, the provisions of Section 2 of the Court’s Requirements for Bar Sponsored Calendar Call Programs apply.</li>
<li>Immediately inform the Chief Judge of any material changes in the information submitted to the Court pursuant to section 1.e., above.
</ol>
""",
                "anchortag": "SEC1",
            },
            {
                "question": "Sec. 2. Appearance and Representation",
                "answer": """A petition, subsequent pleading, motion, or other paper may be filed with the Court through an academic clinic under the following circumstances:
                <ol type="a">
                <li>In any case in which a petition is filed with the Court through an academic clinic, the counsel’s name appearing first on the petition shall be that of the director or clinic practitioner, who shall be designated lead counsel in the case, unless another practitioner who is a member of the Bar of the Court is designated in the petition as lead counsel. The names, Bar numbers, and signatures of other practitioners who are members in good standing of the Bar of the Court may appear on the petition, but the names of students may not so appear. A student may not sign a document submitted to the Court for filing. However, the names of students may appear in the petition or other documents filed in the case to the extent provided in section 3.d. below.</li>
                <li>If a petition has been filed with the Court, and the petitioner is not represented by counsel, an entry of appearance shall be filed with the Court pursuant to Rule 24(a)(3), Tax Court Rules of Practice and Procedure, signed by the director or clinic practitioner, if appropriate, or by any other practitioner who is a member of the Bar of the Court who may be designated as lead counsel in the case.</li>
                <li>All pleadings, motions, stipulations, and other papers (subsequent to the petition) submitted to the Court for filing shall be reviewed and signed by the lead counsel as described in subsections (a) and (b) above.</li>
                <li>A director, clinic practitioner, or other lead counsel who finds it necessary and/or appropriate to withdraw from a case or effectuate a substitution of counsel must comply with the requirements of Rule 24(c) and (d), Tax Court Rules of Practice and Procedure.</li>
                <li>All pleadings, motions, stipulations, notices of trial, and other Court papers shall be brought to the personal attention of the clinic director or clinic practitioner, including situations where another practitioner is acting as lead counsel. When necessary, the Clerk of the Court will make service of any papers, including orders and notices of trial, only upon the lead counsel in accordance with Rule 21(b)(2), Tax Court Rules of Practice and Procedure.</li>
                <li>The director, clinic practitioner, or lead counsel are the only persons who should make contact with the Court in a case described in these requirements. A student participant may not contact the Court concerning a case described in these requirements.</li>
                </ol>
                """,
                "anchortag": "SEC2",
            },
            {
                "question": "Sec. 3. Academic Clinic Contact Information",
                "answer": """If these requirements are satisfied and the Court permits an academic clinic to participate in this program, the Court will use stuffer notices to provide self-represented petitioners with specific contact information for the academic clinic. It is important that the academic clinic immediately notify the Court of any change in director, address or telephone number.""",
                "anchortag": "SEC3",
            },
            {
                "question": "Sec. 4. Termination of Participation",
                "answer": """The Court, in its discretion, may terminate participation in the program by an academic clinic at any time, provided notice stating the cause for the termination is furnished to the academic clinic director. In such a case, counsel of record would be required to file a motion to withdraw, pursuant to Rule 24(c), Tax Court Rules of Practice and Procedure.""",
                "anchortag": "SEC4",
            },
            {
                "question": "Reference Documents",
                "answer": f"""<ul>
                    <li><a href="{docs['2021_letter_to_CJ_academic_law_and_nonlaw.pdf']}" title="Sample Letter">Letter to Chief Judge (Sample): 2021_letter_to_CJ_academic_law_and_nonlaw.pdf</a><br/></li>
                    <li><a href="{docs['stuffer_notice.pdf']}" title="Format for stuffer notice">Stuffer notice: stuffer_notice.pdf</a></li>
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
                        "value": "Requirements for Participation in the United States Tax Court Clinical, Student Practice & Calendar Call Program by Academic Clinics (Non Law School - College or University)",
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
