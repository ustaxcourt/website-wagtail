from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage, CommonText
import logging

logger = logging.getLogger(__name__)


docs = {
    "2021_letter_to_CJ_academic_law_and_nonlaw.pdf": "",
    "clinics_counsel_rooms.pdf": "",
    "stuffer_notice.pdf": "",
}


class ClinicsAcademicPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "clinics-academic"
        title = "Clinics & Pro Bono Programs: Academic Clinical Programs (Law School)"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        for document in docs.keys():
            uploaded_document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=document,
                title=document,
            )
            docs[document] = uploaded_document.file.url

        questions = [
            {
                "question": "Preamble",
                "answer": f"""Many accredited law schools operate academic tax clinics (academic clinics) that provide free legal assistance to low income and self-represented petitioners. Some academic clinics refer such petitioners to outside attorneys who also provide free legal assistance to low income petitioners and participate in a pro bono calendar call program.

                Academic clinics help self-represented petitioners to comply with the Internal Revenue Code and to deal appropriately with the Internal Revenue Service and the Federal courts. The United States Tax Court (the Court) acknowledges the important assistance that academic clinics provide to self-represented petitioners.

                For academic clinics which agree to abide by the requirements stated herein, the Court includes information about the clinic in mailings to self-represented petitioners and permits students enrolled in academic clinics to participate in Court hearings and trials. In addition, in <a href="{docs["clinics_counsel_rooms.pdf"]}" title="Counsel Rooms">25 cities</a> in which the Tax Court holds trial sessions, petitioners' counsel room is reserved for persons admitted to practice before the Court, including attorneys associated with tax clinics and Bar sponsored calendar call programs. The Tax Court does not endorse or recommend any particular clinic or Bar sponsored calendar call program.

                The Court applies the following requirements with regard to academic clinic and student participation in the Court’s academic clinical program.""",
                "anchortag": "PREAMBLE",
            },
            {
                "question": "Sec. 1. Requirements for Participation by Academic Clinics",
                "answer": f"""An academic clinic participating in the Court’s academic clinical program shall not charge any fee for legal services to petitioners. An academic clinic may ask petitioners using its services to reimburse the clinic for incidental costs such as filing fees, copying costs, and postage charges. To participate in the Court’s academic clinical program, an academic clinic shall:
                <ol type="a">
                <li>Constitute a clinical program offered by a law school accredited by the American Bar Association, in which a student receives credit(s) for academic and practice advocacy training. An academic clinic shall be supervised by a director who shall serve as a point of contact for communications to and from the Court. If the director is an adjunct member of the faculty or part-time member of the staff of the sponsoring law school, the signature of a law school administrative official is required on the letter to the Chief Judge (see sec. 1.e.).</li>
                <li>Establish guidelines for screening cases, including therein the objectives of public service and judicial and administrative economy. An academic clinic’s guidelines should be interpreted so that assistance is offered, as appropriate, to low income petitioners who have filed a petition with the Court or who expect to do so.</li>
                <li>Have on staff at least one practitioner (clinic practitioner) who is a member in good standing of the Bar of the Court. All persons associated with the academic clinic shall be informed that the clinic practitioner is personally responsible at all times to the Court and to the taxpayer/petitioner for meeting deadlines, monitoring case preparation, ensuring full compliance with the Court’s Rules of Practice and Procedure and with orders issued by the Court, and, in general, properly preparing a case for hearing, trial, or other disposition. Although the Court recommends that academic clinics provide written notice to petitioners under this provision, and retain a copy of such notice in each case file, there is no need to submit a copy of any such notice to the Court.</li>
                <li>Comply with the U.S. Tax Court Requirements for Nonacademic Clinical Programs if the academic clinic is associated with a nonacademic clinic.</li>
                <li>Submit to the Chief Judge, on or before February 15 of each year, a letter signed by the clinic director (<a href="{docs['2021_letter_to_CJ_academic_law_and_nonlaw.pdf']}" title="Sample Letter">sample</a> format attached) and/or an administrative official of the law school (see sec. 1.a.) which includes (1) the name, address, Tax Court Bar number (if applicable) and contact information (including the e-mail address) of the clinic director and all clinic practitioners; (2) the place(s) of trial served by the clinic; (3) a statement that the academic clinic will comply with these Requirements; (4) a copy of or electronic link to the academic clinic’s guidelines as described in section 1.b., above; (5) whether students are enrolled or otherwise participating in the clinical program spring/summer/fall semester(s), or year round; (6)(a) during the calendar year preceding submission of the letter, an approximate number of petitioners with cases pending in the Court for whom the academic clinic entered an appearance pursuant to Tax Court Rule 24; (b) an approximate number of petitioners who were represented (e.g., through a Power of Attorney) but for whom the academic clinic did not enter an appearance; and (c) an approximate number of petitioners for whom the academic clinic provided consultation, assistance and/or advice (e.g., at the Calendar Call), but did not represent the taxpayer; (7) whether the academic clinic has a relationship with outside attorneys for referral of cases or operation of a calendar call program; (8) any suggestions that the academic clinic may offer for better assisting low income petitioners in their interactions with the Court; (9) an updated one page stuffer notice that the Court can use to notify petitioners of the availability of clinic services for the coming year (<a href="{docs['stuffer_notice.pdf']}" title="Format for stuffer notice">format for stuffer notice</a> attached); and (10) whether the academic clinic would like its stuffer notice to be sent to petitioners in regular tax cases, small tax cases, or both. A version of the stuffer notice written in Spanish may be submitted on the reverse side of the English version. Information about clinics that do not offer assistance in Spanish should not be included in a Spanish language stuffer notice. The Spanish version should include a translation of the following sentence: <strong>"Please be advised that all proceedings in the Tax Court are in English."</strong> The letter to the Chief Judge and updated stuffer notice referred to in this provision may be submitted to the Court in paper form or, if in PDF format, as an attachment to an e-mail using the <a href="mailto:litc@ustaxcourt.gov" title="LITC Contact us">Contact Us</a> link.</li>
                <li>If the academic clinic participates in, or coordinates a calendar call program, the provisions of Section 2 of the Court’s Requirements for Bar Sponsored Calendar Call Programs apply.</li>
                <li>Immediately inform the Chief Judge of any material changes in the information submitted to the Court pursuant to section 1.e., above.</li>
                </ol>""",
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
                "question": "Sec. 3. Student Participation in Court Proceedings",
                "answer": """If the requirements set forth above are satisfied, the Court will permit students who are enrolled in an academic clinic for credit and who are in good standing with the academic institution and law school graduates who are participating in intern/fellowship programs sponsored by an academic institution to participate in proceedings before the Court pursuant to the following procedures:
                <ol type="a">
                <li>Lead counsel who intends to request permission for a student/fellow to participate in proceedings before the Court shall obtain from the petitioner advance written consent for the student/fellow to participate in the case. Although academic clinics should retain a copy of the written consent in each case file, there is no need to submit the consent to the Court.</li>
                <li>When a case described in these requirements is called for hearing or trial, lead counsel shall answer the calendar call, advise the Court whether the case is ready for hearing or trial, and introduce any student/fellow enrolled in the academic clinic who seeks permission to participate in the proceedings.</li>
                <li>If the Court permits a student/fellow to participate in a case upon compliance with subsections (a) and (b), lead counsel shall remain in the courtroom at petitioner’s counsel table at all times during the hearing or trial of the case. A student/fellow who is permitted to participate in a case may, at the discretion of the presiding Judge or Special Trial Judge, present all or any part of a petitioner’s case at a hearing or trial. However, the presiding Judge or Special Trial Judge may at any time exercise the discretion to require the student/fellow to step aside and to require lead counsel to complete the hearing or trial.</li>
                <li>An academic clinic submitting a pleading, motion, stipulation, or other paper to the Court for filing may include a statement in the body of the document including the name of any student/fellow enrolled in the academic clinic who participated in preparation of the document. However, a student/fellow may not sign a document submitted to the Court for filing.</li>
                </ol>
                If the requirements set forth above are satisfied, the Court will permit students who are enrolled in an academic clinic for credit and who are in good standing with the academic institution and law school graduates who are participating in intern/fellowship programs sponsored by an academic institution to participate in proceedings before the Court pursuant to the following procedures: <br/>
                Lead counsel who intends to request permission for a student/fellow to participate in proceedings before the Court shall obtain from the petitioner advance written consent for the student/fellow to participate in the case. Although academic clinics should retain a copy of the written consent in each case file, there is no need to submit the consent to the Court.<br/>
                When a case described in these requirements is called for hearing or trial, lead counsel shall answer the calendar call, advise the Court whether the case is ready for hearing or trial, and introduce any student/fellow enrolled in the academic clinic who seeks permission to participate in the proceedings.<br/>
                If the Court permits a student/fellow to participate in a case upon compliance with subsections (a) and (b), lead counsel shall remain in the courtroom at petitioner’s counsel table at all times during the hearing or trial of the case. A student/fellow who is permitted to participate in a case may, at the discretion of the presiding Judge or Special Trial Judge, present all or any part of a petitioner’s case at a hearing or trial. However, the presiding Judge or Special Trial Judge may at any time exercise the discretion to require the student/fellow to step aside and to require lead counsel to complete the hearing or trial.<br/>
                An academic clinic submitting a pleading, motion, stipulation, or other paper to the Court for filing may include a statement in the body of the document including the name of any student/fellow enrolled in the academic clinic who participated in preparation of the document. However, a student/fellow may not sign a document submitted to the Court for filing.
                """,
                "anchortag": "SEC3",
            },
            {
                "question": "Sec. 4. Academic Clinic Contact Information",
                "answer": """If these requirements are satisfied and the Court permits an academic clinic to participate in this program, the Court will use stuffer notices to provide self-represented petitioners with specific contact information for the academic clinic. It is important that the academic clinic immediately notify the Court of any change in director, address or telephone number.""",
                "anchortag": "SEC4",
            },
            {
                "question": "Sec. 5. Termination of Participation",
                "answer": """The Court, in its discretion, may terminate participation in the program by an academic clinic at any time, provided notice stating the cause for the termination is furnished to the academic clinic director. In such a case, counsel of record would be required to file a motion to withdraw, pursuant to Rule 24(c), Tax Court Rules of Practice and Procedure.""",
                "anchortag": "SEC5",
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
                body=[
                    {
                        "type": "h2",
                        "value": "Requirements for Participation in the United States Tax Court Clinical, Student Practice & Calendar Call Program by Academic Clinics (Law School)",
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
        logger.info(f"Successfully created the '{title}' page.")
