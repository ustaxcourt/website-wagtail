from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import PressRelease

press_releases_docs = {
    "01112021.pdf": "",
    "01122022.pdf": "",
    "01242022.pdf": "",
    "01262022.pdf": "",
    "01222024.pdf": "",
    "01282025.pdf": "",
    "02012022.pdf": "",
    "02122021.pdf": "",
    "02162024.pdf": "",
    "02182022.pdf": "",
    "02212025.pdf": "",
    "02202024.pdf": "",
    "02232021.pdf": "",
    "02252022.pdf": "",
    "03082022.pdf": "",
    "03232022.pdf": "",
    "03142024.pdf": "",
    "03202023.pdf": "",
    "03202023_2.pdf": "",
    "04012022.pdf": "",
    "04052021.pdf": "",
    "04252024.pdf": "",
    "05302024.pdf": "",
    "05172021.pdf": "",
    "05212021.pdf": "",
    "05232021.pdf": "",
    "05082023.pdf": "",
    "05252021.pdf": "",
    "06032022.pdf": "",
    "06242022.pdf": "",
    "07232021.pdf": "",
    "08042023.pdf": "",
    "08082024bv2.pdf": "",
    "08082024v3.pdf": "",
    "08162021.pdf": "",
    "08232022.pdf": "",
    "08252022.pdf": "",
    "08272021.pdf": "",
    "08282023.pdf": "",
    "09232024.pdf": "",
    "10012024.pdf": "",
    "10042024.pdf": "",
    "10052021.pdf": "",
    "10142021.pdf": "",
    "10142022.pdf": "",
    "10162024.pdf": "",
    "10222024.pdf": "",
    "10262022.pdf": "",
    "11192021.pdf": "",
    "11212022.pdf": "",
    "11282023.pdf": "",
    "12062021.pdf": "",
    "12092021.pdf": "",
    "12132024.pdf": "",
    "12142021.pdf": "",
    "12162022.pdf": "",
    "12282021.pdf": "",
}


class PressReleasesPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "press-releases"
        title = "Press Releases"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for doc_name in press_releases_docs.keys():
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )
            press_releases_docs[doc_name] = document

        home_page.add_child(
            instance=PressRelease(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Press Releases",
                body=[
                    {
                        "type": "h3",
                        "value": "2025",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                        <li><a href="{press_releases_docs["02212025.pdf"].file.url}" target="_blank" title="Press Release">02/21/2025</a> - The United States Tax Court announced today that Judge Patrick J. Urda has been elected Chief Judge to serve a two-year term beginning June 1, 2025.</li>
                                        <li><a href="{press_releases_docs["01282025.pdf"].file.url}" target="_blank" title="Press Release">01/28/2025</a> - Tax Court Disciplinary Matters. </li>
                                    </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2024",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                        <li><a href="{press_releases_docs["12132024.pdf"].file.url}" target="_blank" title="Press Release">12/13/2024</a> - Chief Judge Kathleen Kerrigan announced today that Cathy Fung was sworn in as Judge of the United States Tax Court.</li>
                                        <li><a href="{press_releases_docs["10222024.pdf"].file.url}" target="_blank" title="Press Release">10/22/2024</a> - Tax Court Disciplinary Matters. </li>
                                        <li><a href="{press_releases_docs["10162024.pdf"].file.url}" target="_blank" title="Press Release">10/16/2024</a> - Chief Judge Kathleen Kerrigan announced today that Rose E. Jenkins was sworn in as Judge of the United States Tax Court.</li>
                                        <li><a href="{press_releases_docs["10042024.pdf"].file.url}" target="_blank" title="Press Release">10/04/2024</a> - Chief Judge Kathleen Kerrigan announced today that Jeffrey S. Arbeit and Benjamin A. Guider III were sworn in as Judges of the United States Tax Court.</li>
                                        <li><a href="{press_releases_docs["10012024.pdf"].file.url}" target="_blank" title="Press Release">10/01/2024</a> - Chief Judge Kerrigan announced the retirement of Judge Joseph H. Gale</li>
                                        <li><a href="{press_releases_docs["09232024.pdf"].file.url}" target="_blank" title="Press Release">09/23/2024</a> - Tax Court Disciplinary Matters</li>
                                        <li><a href="{press_releases_docs["08082024bv2.pdf"].file.url}" target="_blank" title="Press Release">08/08/2024</a> - Chief Judge Kathleen Kerrigan announced today that Kashi Way and Adam B. Landy were sworn in as Judges of the United States Tax Court.</li>
                                        <li><a href="{press_releases_docs["08082024v3.pdf"].file.url}" target="_blank" title="Press Release">08/08/2024</a> - Chief Judge Kathleen Kerrigan announced today that the United States Tax Court has adopted final amendments to its Rules of Practice and Procedure.</li>
                                        <li><a href="{press_releases_docs["05302024.pdf"].file.url}" target="_blank" title="Press Release">05/30/2024</a> - Tax Court Disciplinary Matters</li>
                                        <li><a href="{press_releases_docs["04252024.pdf"].file.url}" target="_blank" title="Press Release">04/25/2024</a> - Charles Jeane becomes Clerk of the Court.</li>
                                        <li><a href="{press_releases_docs["03142024.pdf"].file.url}" target="_blank" title="Press Release">03/14/2024</a> - In Memory of Judge John O. Colvin.</li>
                                        <li><a href="{press_releases_docs["02202024.pdf"].file.url}" target="_blank" title="Press Release">02/20/2024</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["02162024.pdf"].file.url}" target="_blank" title="Press Release">02/16/2024</a> - The Court announced today that Chief Judge Kathleen Kerrigan has been re-elected and will serve another two-year term beginning June 1, 2024.</li>
                                       <li><a href="{press_releases_docs["01222024.pdf"].file.url}" target="_blank" title="Press Release"> 01/22/2024</a> - Chief Judge Kathleen Kerrigan announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.</li>
                                    </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2023",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                        <li><a href="{press_releases_docs["11282023.pdf"].file.url}" target="_blank" title="Press Release">11/28/2023</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["08282023.pdf"].file.url}" target="_blank" title="Press Release">08/28/2023</a> - Chief Judge Kathleen Kerrigan announced that Jennifer E. Siegel and Zachary S. Fried have been selected to serve as Special Trial Judges of the United States Tax Court.</li>
                                        <li><a href="{press_releases_docs["08042023.pdf"].file.url}" target="_blank" title="Press Release">08/04/2023</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["05082023.pdf"].file.url}" target="_blank" title="Press Release">05/08/2023</a> - The U.S. Tax Court announced that the written examination for applicants other than attorneys at law (nonattorney applicants) for admission to practice before the U.S. Tax Court will be held remotely at 12:30pm EST on Wednesday, November 8, 2023, using the ExamSoft platform.</li>
                                        <li><a href="{press_releases_docs["03202023_2.pdf"].file.url}" target="_blank" title="Press Release">03/20/2023</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["03202023.pdf"].file.url}" target="_blank" title="Press Release">03/20/2023</a> - Chief Judge Kathleen Kerrigan announced today that the United States Tax Court has adopted final amendments to its Rules of Practice and Procedure.</li>
                                    </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2022",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                        <li><a href="{press_releases_docs["12162022.pdf"].file.url}" target="_blank" title="Press Release">12/16/2022</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["11212022.pdf"].file.url}" target="_blank" title="Press Release">11/21/2022</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["10262022.pdf"].file.url}" target="_blank" title="Press Release">10/26/2022</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["10142022.pdf"].file.url}" target="_blank" title="Press Release">10/14/2022</a> - In Memory of Judge Herbert Chabot.</li>
                                        <li><a href="{press_releases_docs["08252022.pdf"].file.url}" target="_blank" title="Press Release">08/25/2022</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["08232022.pdf"].file.url}" target="_blank" title="Press Release">08/23/2022</a> - The U.S. Tax Court has issued Administrative Order 2022-01, which repeals Administrative Orders 2021-02 and 2021-03, effective August 29, 2022.</li>
                                        <li><a href="{press_releases_docs["06242022.pdf"].file.url}" target="_blank" title="Press Release">06/24/2022</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["06032022.pdf"].file.url}" target="_blank" title="Press Release">06/03/2022</a> - Beginning June 6, 2022, the Tax Court’s Washington, D.C. courthouse will be open to the public.</li>
                                        <li><a href="{press_releases_docs["04012022.pdf"].file.url}" target="_blank" title="Press Release">04/01/2022</a> - Chief Judge Maurice B. Foley announced today that, effective March 31, 2022, Special Trial Judge Daniel A. Guy, Jr. has retired.</li>
                                        <li><a href="{press_releases_docs["03232022.pdf"].file.url}" target="_blank" title="Press Release">03/23/2022</a> - Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.</li>
                                        <li><a href="{press_releases_docs["03082022.pdf"].file.url}" target="_blank" title="Press Release">03/08/2022</a> - In Memory of Judge Joel Gerber</li>
                                        <li><a href="{press_releases_docs["02252022.pdf"].file.url}" target="_blank" title="Press Release">02/25/2022</a> - The United States Tax Court announced today that Judge Kathleen Kerrigan has been elected Chief Judge to serve a two-year term beginning June 1, 2022.</li>
                                        <li><a href="{press_releases_docs["02182022.pdf"].file.url}" target="_blank" title="Press Release"> 02/18/2022</a> - In Memory of Judge Robert P. Ruwe</li>
                                        <li><a href="{press_releases_docs["02012022.pdf"].file.url}" target="_blank" title="Press Release"> 02/02/2022</a> - Since December 28, 2020, over 750 new features have been added to DAWSON, the Tax Court’s case-management system.</li>
                                        <li><a href="{press_releases_docs["01262022.pdf"].file.url}" target="_blank" title="Press Release"> 01/26/2022</a> - After assessing public health and other factors relating to nationwide COVID-19 cases, the U.S. Tax Court has determined that it is not appropriate to conduct in-person proceedings through February 25, 2022.</li>
                                        <li><a href="{press_releases_docs["01242022.pdf"].file.url}" target="_blank" title="Press Release">01/24/2022</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["01122022.pdf"].file.url}" target="_blank" title="Press Release">01/12/2022</a> - After assessing public health and other factors relating to the rapid nationwide increase of COVID-19 cases, the U.S. Tax Court has determined that it is not appropriate to conduct in-person proceedings in January 2022.</li>
                                    </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2021",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                        <li><a href="{press_releases_docs["12282021.pdf"].file.url}" target="_blank" title="Press Release">12/28/2021</a> - Chief Judge Maurice B. Foley announced today that opinion search is now available in the DAWSON case management system.</li>
                                        <li><a href="{press_releases_docs["12142021.pdf"].file.url}" target="_blank" title="Press Release">12/14/2021</a> - Chief Judge Maurice B. Foley announced today that order search is now available in the DAWSON case management system.</li>
                                        <li><a href="{press_releases_docs["12092021.pdf"].file.url}" target="_blank" title="Press Release">12/09/2021</a> - From January 1, 2021, through November 30, 2021, the Court received 33,300 petitions.</li>
                                        <li><a href="{press_releases_docs["12062021.pdf"].file.url}" target="_blank" title="Press Release">12/06/2021</a> - On December 6, 2021, Chief Judge Maurice B. Foley announced that Adam B. Landy and Eunkyong Choi have each been selected to serve as a Special Trial Judge and taken the oath of office.</li>
                                        <li><a href="{press_releases_docs["11192021.pdf"].file.url}" target="_blank" title="Press Release">11/19/2021</a> - On November 18, 2021, Special Trial Judge Daniel A. Guy, Jr. received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.</li>
                                        <li><a href="{press_releases_docs["10142021.pdf"].file.url}" target="_blank" title="Press Release">10/14/2021</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["10052021.pdf"].file.url}" target="_blank" title="Press Release"> 10/05/2021</a> - To provide guidance with respect to in-person proceedings, the Court has posted a new publication, Court Standards and Protocols to Protect Public Health, as well as issued Administrative Order 2021-02, Washington, D.C. Courthouse Access.</li>
                                       <li><a href="{press_releases_docs["08272021.pdf"].file.url}" target="_blank" title="Press Release"> 08/27/2021</a> - On August 27, 2021, the Court issued Administrative Order 2021-01, Policies for Remote (Virtual) Proceedings, which outlines the policies adopted allowing for both in-person and remote (virtual) trials.</li>
                                        <li><a href="{press_releases_docs["08162021.pdf"].file.url}" target="_blank" title="Press Release">08/16/2021</a> - The Court met with various stakeholders to address concerns relating to the increased number of petitions being filed and to limit the potential for premature assessment and enforcement action.</li>
                                        <li><a href="{press_releases_docs["07232021.pdf"].file.url}" target="_blank" title="Press Release">07/23/2021</a> - The United States Tax Court has received a significantly higher number of petitions this year. The Court is processing petitions expeditiously, but the increased volume has caused a delay between when a petition is received by the Court and when it is served on the Internal Revenue Service.</li>
                                        <li><a href="{press_releases_docs["05212021.pdf"].file.url}" target="_blank" title="Press Release">05/21/2021</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["05172021.pdf"].file.url}" target="_blank" title="Press Release"> 05/17/2021</a> - The United States Tax Court announced today that the examination for admission to practice before the Court will be held remotely on Wednesday, November 17, 2021.</li>
                                       <li><a href="{press_releases_docs["04052021.pdf"].file.url}" target="_blank" title="Press Release"> 04/05/2021</a> - Chief Judge Maurice B. Foley announced today that the United States Tax Court will begin accepting applications for its new Diversity in Government Internship Program (DiG Tax).</li>
                                       <li><a href="{press_releases_docs["02232021.pdf"].file.url}" target="_blank" title="Press Release"> 02/23/2021</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["02122021.pdf"].file.url}" target="_blank" title="Press Release"> 02/12/2021</a> - The Tax Court announces its Diversity & Inclusion Series. The series is comprised of webinars that will spotlight different trailblazers and their paths to, and success in, the field of tax law.</li>
                                       <li><a href="{press_releases_docs["01112021.pdf"].file.url}" target="_blank" title="Press Release"> 01/11/2021</a> - Chief Judge Maurice B. Foley announced today that DAWSON has been updated to include “Today’s Orders”.</li>
                                    </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": """<a role="button" tabindex="0" href="/press-releases/archives" target="_blank" title="Press Release Archives">Archive</a>""",
                    },
                ],
                show_in_menus=True,
            )
        )
