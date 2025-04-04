from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import PressRelease

press_releases_docs = {
    "01152020.pdf": "",
    "01112021.pdf": "",
    "01122022.pdf": "",
    "011116.pdf": "",
    "011702.pdf": "",
    "112009.pdf": "",
    "011508.pdf": "",
    "011207.pdf": "",
    "01242022.pdf": "",
    "01262022.pdf": "",
    "01222024.pdf": "",
    "01282025.pdf": "",
    "02012022.pdf": "",
    "02122021.pdf": "",
    "022502.pdf": "",
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
    "040402.pdf": "",
    "040307.pdf": "",
    "04012022.pdf": "",
    "04052021.pdf": "",
    "04252024.pdf": "",
    "05302024.pdf": "",
    "05182020.pdf": "",
    "05172021.pdf": "",
    "05212021.pdf": "",
    "05232021.pdf": "",
    "05082023.pdf": "",
    "05252021.pdf": "",
    "050511.pdf": "",
    "06032022.pdf": "",
    "06242022.pdf": "",
    "063003.pdf": "",
    "071519.pdf": "",
    "070612.pdf": "",
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
    "091809.pdf": "",
    "092105.pdf": "",
    "100308.pdf": "",
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
    "010301.pdf": "",
    "010318.pdf": "",
    "010501.pdf": "",
    "011607.pdf": "",
    "012619.pdf": "",
    "012706.pdf": "",
    "020419.pdf": "",
    "021003.pdf": "",
    "021607_release.pdf": "",
    "021717.pdf": "",
    "021916.pdf": "",
    "022300.pdf": "",
    "022304.pdf": "",
    "022415.pdf": "",
    "022618.pdf": "",
    "022800.pdf": "",
    "022806.pdf": "",
    "022916.pdf": "",
    "030612.pdf": "",
    "031519.pdf": "",
    "031811.pdf": "",
    "032000.pdf": "",
    "032416.pdf": "",
    "032612.pdf": "",
    "032709.pdf": "",
    "032816.pdf": "",
    "041300.pdf": "",
    "041317.pdf": "",
    "041712.pdf": "",
    "041918.pdf": "",
    "042203_Goeke.pdf": "",
    "042203_Haines.pdf": "",
    "042415.pdf": "",
    "042514.pdf": "",
    "042607.pdf": "",
    "042619.pdf": "",
    "042700.pdf": "",
    "042803_Wherry.pdf": "",
    "042804.pdf": "",
    "043008.pdf": "",
    "043012.pdf": "",
    "050306.pdf": "",
    "050616.pdf": "",
    "050712.pdf": "",
    "050812.pdf": "",
    "050818.pdf": "",
    "051019.pdf": "",
    "051217.pdf": "",
    "051314.pdf": "",
    "051704_Electronic_Courtroom.pdf": "",
    "051719.pdf": "",
    "052915.pdf": "",
    "053116.pdf": "",
    "060208.pdf": "",
    "061119.pdf": "",
    "061212.pdf": "",
    "061416.pdf": "",
    "061703_Kroupa.pdf": "",
    "061711.pdf": "",
    "062005.pdf": "",
    "062304.pdf": "",
    "062513.pdf": "",
    "062612.pdf": "",
    "063003_Holmes.pdf": "",
    "070115.pdf": "",
    "070705.pdf": "",
    "071219.pdf": "",
    "071312.pdf": "",
    "071814.pdf": "",
    "071816.pdf": "",
    "072018.pdf": "",
    "080108_Paris.pdf": "",
    "080408_Gustafson.pdf": "",
    "080615.pdf": "",
    "083007.pdf": "",
    "083117.pdf": "",
    "090105.pdf": "",
    "090419.pdf": "",
    "090514.pdf": "",
    "090618.pdf": "",
    "091112.pdf": "",
    "091206.pdf": "",
    "091517.pdf": "",
    "091812.pdf": "",
    "092319.pdf": "",
    "092418.pdf": "",
    "092518.pdf": "",
    "093013.pdf": "",
    "100908_Morrison.pdf": "",
    "101014.pdf": "",
    "101216.pdf": "",
    "101218.pdf": "",
    "101317.pdf": "",
    "101515.pdf": "",
    "102005.pdf": "",
    "10062020.pdf": "",
    "110204.pdf": "",
    "110601.pdf": "",
    "111414.pdf": "",
    "112219.pdf": "",
    "112519.pdf": "",
    "112707.pdf": "",
    "112806.pdf": "",
    "113018.pdf": "",
    "113018_disciplinary_matters.pdf": "",
    "120301.pdf": "",
    "120605.pdf": "",
    "121205_electronic_filing.pdf": "",
    "121815.pdf": "",
    "121914.pdf": "",
    "122010.pdf": "",
    "121616.pdf": "",
    "122013.pdf": "",
    "121918.pdf": "",
    "122117.pdf": "",
    "122310.pdf": "",
    "122707.pdf": "",
    "122811.pdf": "",
    "02212020.pdf": "",
    "02242020.pdf": "",
    "03112020.pdf": "",
    "03132020.pdf": "",
    "03182020.pdf": "",
    "03232020.pdf": "",
    "04212020_1.pdf": "",
    "04212020_2.pdf": "",
    "05042020.pdf": "",
    "05052010_exam.pdf": "",
    "05072020.pdf": "",
    "05292020_copywork.pdf": "",
    "05292020_proceedings.pdf": "",
    "06192020.pdf": "",
    "06222020.pdf": "",
    "06242020.pdf": "",
    "07172020.pdf": "",
    "07202020.pdf": "",
    "08062020.pdf": "",
    "08172020.pdf": "",
    "09092020.pdf": "",
    "10072020.pdf": "",
    "10292020.pdf": "",
    "11122020.pdf": "",
    "11162020.pdf": "",
    "11302020.pdf": "",
    "12102020.pdf": "",
    "11202020.pdf": "",
    "12182020.pdf": "",
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
                        "type": "button",
                        "value": {
                            "text": "Archive",
                            "href": "/press-releases/archives",
                            "style": "primary",
                        },
                    },
                    {"type": "h2", "value": "Press Release Archives "},
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2020",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["12182020.pdf"].file.url}" target="_blank" title="Press Release"> 12/18/2020</a> - Chief Judge Maurice B. Foley announced today that on December 28, 2020, the United States Tax Court will officially launch DAWSON (Docket Access Within a Secure Online Network), its new case management system.</li>
                                        <li><a href="{press_releases_docs["12102020.pdf"].file.url}" target="_blank" title="Press Release">12/10/2020</a> - Chief Judge Maurice B. Foley announced today that the Court has updated its guidance on procedures related to subpoenas for remote proceedings.</li>
                                        <li><a href="{press_releases_docs["11302020.pdf"].file.url}" target="_blank" title="Press Release">11/30/2020</a> - Senior Judge Robert P. Ruwe has fully retired and is no longer recalled for judicial service.</li>
                                        <li><a href="{press_releases_docs["11202020.pdf"].file.url}" target="_blank" title="Press Release">11/20/2020</a> - For paper documents requiring multiple signatures and postmarked November 21, 2020 through December 28, 2020, the Court has modified its signature requirements as outlined in Administrative Order 2020-05.</li>
                                        <li><a href="{press_releases_docs["11162020.pdf"].file.url}" target="_blank" title="Press Release">11/16/2020</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["11122020.pdf"].file.url}" target="_blank" title="Press Release">11/12/2020</a> - Beginning Monday, November 16, 2020, the Court will resume accepting hand-delivered documents to the main courthouse building.</li>
                                       <li><a href="{press_releases_docs["10292020.pdf"].file.url}" target="_blank" title="Press Release"> 10/29/2020</a> - Effective Friday, October 30, 2020, and until further notice, the United States Tax Court will be suspending its in-person acceptance of hand-delivered documents.</li>
                                        <li><a href="{press_releases_docs["10072020.pdf"].file.url}" target="_blank" title="Press Release">10/07/2020</a> - To facilitate the transition to the Court's new case management system, beginning at 5:00 PM Eastern Time on November 20, 2020, the current e-filing system will become inaccessible and all electronic files will become read-only.</li>
                                        <li><a href="{press_releases_docs["10062020.pdf"].file.url}" target="_blank" title="Press Release">10/06/2020</a> - Chief Judge Maurice B. Foley announced that the United States Tax Court has adopted amendments to its Rules of Practice and Procedure.</li>
                                       <li><a href="{press_releases_docs["09092020.pdf"].file.url}" target="_blank" title="Press Release"> 09/09/2020</a> - Chief Special Trial Judge Lewis R. Carluzzo received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.</li>
                                       <li><a href="{press_releases_docs["08172020.pdf"].file.url}" target="_blank" title="Press Release"> 08/17/2020</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["08062020.pdf"].file.url}" target="_blank" title="Press Release"> 08/06/2020</a> - Chief Judge Maurice B. Foley announced additional guidance with respect to remote proceedings.</li>
                                        <li><a href="{press_releases_docs["07202020.pdf"].file.url}" target="_blank" title="Press Release">07/20/2020</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["07172020.pdf"].file.url}" target="_blank" title="Press Release"> 07/17/2020</a> - Chief Judge Maurice B. Foley announced that, effective July 16, 2020, Senior Judge Joel Gerber has retired and is no longer recalled for judicial service.</li>
                                       <li><a href="{press_releases_docs["06242020.pdf"].file.url}" target="_blank" title="Press Release"> 06/24/2020</a> - Beginning July 10, 2020, the Clerk’s Office will accept hand-delivered documents between the hours of 8:00 AM and 4:30 PM, Monday through Friday.</li>
                                       <li><a href="{press_releases_docs["06222020.pdf"].file.url}" target="_blank" title="Press Release"> 06/22/2020</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["06192020.pdf"].file.url}" target="_blank" title="Press Release"> 06/19/2020</a> - Mail delivery will resume on July 10, 2020.</li>
                                       <li><a href="{press_releases_docs["05292020_copywork.pdf"].file.url}" target="_blank" title="Press Release"> 05/29/2020</a> - To accommodate continuing uncertainties relating to the COVID-19 pandemic, and until further notice, Court proceedings will be conducted remotely.</li>
                                       <li><a href="{press_releases_docs["05292020_proceedings.pdf"].file.url}" target="_blank" title="Press Release"> 05/29/2020</a> - The Court will resume accepting requests for photocopies of Court records from non- parties (copy requests) on June 1, 2020.</li>
                                       <li><a href="{press_releases_docs["05182020.pdf"].file.url}" target="_blank" title="Press Release"> 05/18/2020</a> - Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.</li>
                                        <li><a href="{press_releases_docs["05072020.pdf"].file.url}" target="_blank" title="Press Release">05/07/2020</a> - To mitigate risks and concerns related to COVID-19, the Court is postponing the November 2020 nonattorney examination to the fall of 2021.</li>
                                        <li><a href="{press_releases_docs["05042020.pdf"].file.url}" target="_blank" title="Press Release">05/04/2020</a> - The Court announced that attorney applications for admission to practice before the Court may be emailed to the Admissions Office.</li>
                                        <li><a href="{press_releases_docs["04212020_1.pdf"].file.url}" target="_blank" title="Press Release">04/21/2020</a> - Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.</li>
                                        <li><a href="{press_releases_docs["04212020_2.pdf"].file.url}" target="_blank" title="Press Release">04/21/2020</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["03232020.pdf"].file.url}" target="_blank" title="Press Release">03/23/2020</a> - The United States Tax Court building remains closed and trial sessions through June 30, 2020 are canceled.</li>
                                       <li><a href="{press_releases_docs["03182020.pdf"].file.url}" target="_blank" title="Press Release"> 03/18/2020</a> - The Court announced that effective as of 9:00 PM on March 18, 2020, and until further notice, the United States Tax Court building is closed.</li>
                                       <li><a href="{press_releases_docs["03132020.pdf"].file.url}" target="_blank" title="Press Release"> 03/13/2020</a> - The Court has determined that it is appropriate to cancel certain trial sessions and to close the Court to visitors, effective immediately.</li>
                                        <li><a href="{press_releases_docs["03112020.pdf"].file.url}" target="_blank" title="Press Release">03/11/2020</a> - The Court has determined that it is appropriate to cancel certain trial sessions.</li>
                                       <li><a href="{press_releases_docs["02242020.pdf"].file.url}" target="_blank" title="Press Release"> 02/24/2020</a> - The Court announced that Chief Judge Maurice B. Foley has been re-elected and will serve another two-year term beginning June 1, 2020.</li>
                                       <li><a href="{press_releases_docs["02212020.pdf"].file.url}" target="_blank" title="Press Release"> 02/21/2020</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["01152020.pdf"].file.url}" target="_blank" title="Press Release"> 01/15/2020</a> - The Tax Court has adopted amendments to its Rules of Practice and Procedure.</li>
                                    </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2019",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                        <li><a href="{press_releases_docs["112519.pdf"].file.url}" target="_blank" title="Press Release">11/25/2019</a> - Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.</li>
                                       <li><a href="{press_releases_docs["112219.pdf"].file.url}" target="_blank" title="Press Release"> 11/22/2019</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["092319.pdf"].file.url}" target="_blank" title="Press Release">09/23/2019</a> - In Memory of Judge Arthur L. Nims III.</li>
                                        <li><a href="{press_releases_docs["090419.pdf"].file.url}" target="_blank" title="Press Release">09/04/2019</a> - Chief Judge Maurice B. Foley announced the retirement of Special Trial Judge Robert N. Armen, Jr.</li>
                                        <li><a href="{press_releases_docs["071519.pdf"].file.url}" target="_blank" title="Press Release">07/15/2019</a> - The Tax Court has adopted amendments to its Rules of Practice and Procedure.</li>
                                        <li><a href="{press_releases_docs["071219.pdf"].file.url}" target="_blank" title="Press Release">07/12/2019</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["061119.pdf"].file.url}" target="_blank" title="Press Release"> 06/11/2019</a> - On June 11, 2019, Chief Judge Maurice B. Foley announced that, effective as of June 7, 2019, Senior Judge Julian I. Jacobs has fully retired and is no longer recalled for judicial service.</li>
                                        <li><a href="{press_releases_docs["051719.pdf"].file.url}" target="_blank" title="Press Release">05/17/2019</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["051019.pdf"].file.url}" target="_blank" title="Press Release">05/10/2019</a> - The Court issued Administrative Order No. 2019-01, outlining procedures for filing limited entries of appearance in Tax Court cases.</li>
                                       <li><a href="{press_releases_docs["042619.pdf"].file.url}" target="_blank" title="Press Release"> 04/26/2019</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["031519.pdf"].file.url}" target="_blank" title="Press Release">03/15/2019</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["020419.pdf"].file.url}" target="_blank" title="Press Release"> 02/04/2019</a> - The Tax Court has extended the period for submission of comments regarding interim and proposed partnership rules.</li>
                                       <li><a href="{press_releases_docs["012619.pdf"].file.url}" target="_blank" title="Press Release"> 01/26/2019</a> - Chief Judge Maurice B. Foley announced the resumption of full operations of the United States Tax Court effective Monday, January 28, 2019.</li>
                                        </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2018",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["121918.pdf"].file.url}" target="_blank" title="Press Release">12/19/2018</a> - The Tax Court has announced interim and proposed amendments to its Rules of Practice and Procedure.</li>
                                       <li><a href="{press_releases_docs["113018.pdf"].file.url}" target="_blank" title="Press Release">11/30/2018</a> - The Tax Court has adopted amendments to its Rules of Practice and Procedure.</li>
                                       <li><a href="{press_releases_docs["113018_disciplinary_matters.pdf"].file.url}" target="_blank" title="Press Release">11/30/2018</a> - Tax Court Disciplinary Matters.</li>
                                      <li><a href="{press_releases_docs["101218.pdf"].file.url}" target="_blank" title="Press Release"> 10/12/2018</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["092518.pdf"].file.url}" target="_blank" title="Press Release">09/25/2018</a> - In Memory of Judge David Laro.</li>
                                       <li><a href="{press_releases_docs["092418.pdf"].file.url}" target="_blank" title="Press Release">09/24/2018</a> - Chief Judge Maurice B. Foley announced the retirement of Judge Carolyn P. Chiechi.</li>
                                       <li><a href="{press_releases_docs["090618.pdf"].file.url}" target="_blank" title="Press Release">09/06/2018</a> - Tax Court Disciplinary Matters.</li>
                                      <li><a href="{press_releases_docs["072018.pdf"].file.url}" target="_blank" title="Press Release"> 07/20/2018</a> - Tax Court Disciplinary Matters.</li>
                                      <li><a href="{press_releases_docs["050818.pdf"].file.url}" target="_blank" title="Press Release"> 05/08/2018</a> - The Tax Court has issued a press release announcing the date and time of the 2018 written exam for admission to practice for applicants other than attorneys at law.</li>
                                       <li><a href="{press_releases_docs["041918.pdf"].file.url}" target="_blank" title="Press Release">04/19/2018</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["022618.pdf"].file.url}" target="_blank" title="Press Release">02/26/2018</a> - Judge Maurice B. Foley will become Chief Judge June 1, 2018.</li>
                                      <li><a href="{press_releases_docs["010318.pdf"].file.url}" target="_blank" title="Press Release"> 01/03/2018</a> - Chief Judge L. Paige Marvel announced the retirement of Judge Robert A. Wherry, Jr.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2017",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["122117.pdf"].file.url}" target="_blank" title="Press Release">12/21/2017</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["101317.pdf"].file.url}" target="_blank" title="Press Release">10/13/2017</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["091517.pdf"].file.url}" target="_blank" title="Press Release">09/15/2017</a> - The 2018 Tax Court Judicial Conference will be held in Chicago, Illinois, on the campus of Northwestern University’s Pritzker School of Law in March.</li>
                                       <li><a href="{press_releases_docs["083117.pdf"].file.url}" target="_blank" title="Press Release">08/31/2017</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["051217.pdf"].file.url}" target="_blank" title="Press Release">05/12/2017</a> - The Tax Court announced that Chief Special Trial Judge Peter J. Panuthos has decided to step down as Chief Special Trial Judge, effective September 1, 2017, and that Special Trial Judge Lewis R. Carluzzo has been named Chief Special Trial Judge, effective September 1, 2017.</li>
                                       <li><a href="{press_releases_docs["041317.pdf"].file.url}" target="_blank" title="Press Release">04/13/2017</a> - Tax Court Disciplinary Matters.</li>
                                      <li><a href="{press_releases_docs["021717.pdf"].file.url}" target="_blank" title="Press Release"> 02/17/2017</a> - Tax Court Disciplinary Matters.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2016",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["121616.pdf"].file.url}" target="_blank" title="Press Release">12/16/2016</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["101216.pdf"].file.url}" target="_blank" title="Press Release">10/12/2016</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["071816.pdf"].file.url}" target="_blank" title="Press Release">07/18/2016</a> - Chief Judge L. Paige Marvel has released a statement acknowledging the passing on July 15, 2016, of the Honorable Howard A. Dawson, Jr., the longest-serving judge in Tax Court history.</li>
                                       <li><a href="{press_releases_docs["061416.pdf"].file.url}" target="_blank" title="Press Release">06/14/2016</a> - The Chief Judge has announced the adoption of Rules for Judicial Conduct and Disability Proceedings for the United States Tax Court.</li>
                                       <li><a href="{press_releases_docs["053116.pdf"].file.url}" target="_blank" title="Press Release">05/31/2016</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["050616.pdf"].file.url}" target="_blank" title="Press Release">05/06/2016</a> - The Tax Court has issued a press release announcing the date and time of the 2016 written exam for admission to practice for applicants other than attorneys at law.</li>
                                       <li><a href="{press_releases_docs["032816.pdf"].file.url}" target="_blank" title="Press Release">03/28/2016</a> - The Tax Court has announced interim and proposed amendments to its Rules of Practice and Procedure.</li>
                                       <li><a href="{press_releases_docs["032416.pdf"].file.url}" target="_blank" title="Press Release">03/24/2016</a> - Diana L. Leyden to be sworn in as a Special Trial Judge.</li>
                                       <li><a href="{press_releases_docs["022916.pdf"].file.url}" target="_blank" title="Press Release">02/29/2016</a> - Judge L. Paige Marvel will become Chief Judge June 1, 2016.</li>
                                       <li><a href="{press_releases_docs["021916.pdf"].file.url}" target="_blank" title="Press Release"> 02/19/2016</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["011116.pdf"].file.url}" target="_blank" title="Press Release"> 01/11/2016</a> - The Tax Court has announced proposed amendments to its Rules of Practice and Procedure.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2015",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["121815.pdf"].file.url}" target="_blank" title="Press Release">12/18/15</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["101515.pdf"].file.url}" target="_blank" title="Press Release">10/15/15</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["080615.pdf"].file.url}" target="_blank" title="Press Release">08/06/15</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["070115.pdf"].file.url}" target="_blank" title="Press Release">07/01/15</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["052915.pdf"].file.url}" target="_blank" title="Press Release">05/29/15</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["042415.pdf"].file.url}" target="_blank" title="Press Release">04/24/15</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["022415.pdf"].file.url}" target="_blank" title="Press Release"> 02/24/15</a> - Tax Court Disciplinary Matters.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2014",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["121914.pdf"].file.url}" target="_blank" title="Press Release">12/19/14</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["111414.pdf"].file.url}" target="_blank" title="Press Release">11/14/14</a> - Tax Court Disciplinary Matters.</li>
                                       <li><a href="{press_releases_docs["101014.pdf"].file.url}" target="_blank" title="Press Release">10/10/14</a> - The Court issued a press release in Amazon.Com, Inc. & Subsidiaries v. Commissioner of Internal Revenue.</li>
                                       <li><a href="{press_releases_docs["090514.pdf"].file.url}" target="_blank" title="Press Release">09/05/14</a> - Tax Court Disciplinary Matters.</li>
                                      <li><a href="{press_releases_docs["071814.pdf"].file.url}" target="_blank" title="Press Release"> 07/18/14</a> - Tax Court Disciplinary Matters.</li>
                                      <li><a href="{press_releases_docs["051314.pdf"].file.url}" target="_blank" title="Press Release"> 05/13/14</a> - The Tax Court has issued a press release announcing the date and time of the 2014 written exam for admission to practice for applicants other than attorneys at law.</li>
                                      <li><a href="{press_releases_docs["042514.pdf"].file.url}" target="_blank" title="Press Release"> 04/25/14</a> - Tax Court Disciplinary Matters.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2013",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                        <li><a href="{press_releases_docs["122013.pdf"].file.url}" target="_blank" title="Press Release">12/20/13</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["093013.pdf"].file.url}" target="_blank" title="Press Release">09/30/13</a> - Tax Court Disciplinary Matters.</li>
                                        <li><a href="{press_releases_docs["062513.pdf"].file.url}" target="_blank" title="Press Release">06/25/13</a> - Tax Court Disciplinary Matters.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2012",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                         <li><a href="{press_releases_docs["091812.pdf"].file.url}" target="_blank" title="Press Release">09/18/12</a> - In Memory of Judge Russell E. Train.</li>
                                         <li><a href="{press_releases_docs["091112.pdf"].file.url}" target="_blank" title="Press Release"> 09/11/12</a> - In Memory of Judge Lapsley W. Hamblen, Jr.</li>
                                         <li><a href="{press_releases_docs["071312.pdf"].file.url}" target="_blank" title="Press Release">07/13/12</a> - In Memory of Judge Renato Beghe.</li>
                                         <li><a href="{press_releases_docs["070612.pdf"].file.url}" target="_blank" title="Press Release">07/06/12</a> - The Tax Court has adopted amendments to its Rules of Practice and Procedure requiring electronic filing by most practitioners, providing privacy protections in whistleblower cases, and making other miscellaneous and conforming changes.</li>
                                         <li><a href="{press_releases_docs["062612.pdf"].file.url}" target="_blank" title="Press Release"> 06/26/12</a> - The Tax Court announces a uniform method of spot-citing Memorandum Opinions.</li>
                                         <li><a href="{press_releases_docs["061212.pdf"].file.url}" target="_blank" title="Press Release">06/12/12</a> - The Tax Court announces the investiture of Judge Kathleen Kerrigan.</li>
                                         <li><a href="{press_releases_docs["050812.pdf"].file.url}" target="_blank" title="Press Release">05/08/12</a> - The Tax Court has issued a press release announcing the date and time of the 2012 written exam for admission to practice for applicants other than attorneys at law.</li>
                                         <li><a href="{press_releases_docs["050712.pdf"].file.url}" target="_blank" title="Press Release">05/07/12</a> - Judge Michael B. Thornton has been elected as Chief Judge of the United States Tax Court to serve a 2-year term beginning June 1, 2012.</li>
                                         <li><a href="{press_releases_docs["043012.pdf"].file.url}" target="_blank" title="Press Release">04/30/12</a> - Judge Robert P. Ruwe received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.</li>
                                         <li><a href="{press_releases_docs["041712.pdf"].file.url}" target="_blank" title="Press Release">04/17/12</a> - Daniel A. Guy, Jr., will take the oath of office to serve as a Special Trial Judge of the United States Tax Court on May 31, 2012.</li>
                                         <li><a href="{press_releases_docs["032612.pdf"].file.url}" target="_blank" title="Press Release"> 03/26/12</a> - Chief Special Trial Judge Peter J. Panuthos received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.</li>
                                         <li><a href="{press_releases_docs["030612.pdf"].file.url}" target="_blank" title="Press Release"> 03/06/12</a> - Comments received on proposed amendments to the Tax Court Rules of Practice and Procedure requiring electronic filing by most parties represented by counsel, providing privacy protections in whistleblower cases, and making other miscellaneous and conforming changes.</li>
                                         </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2011",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["122811.pdf"].file.url}" target="_blank" title="Press Release">12/28/11</a> - The Tax Court has announced proposed amendments to its Rules of Practice and Procedure reducing the number of copies required for papers filed with the Court, requiring electronic filing by most parties represented by counsel, providing privacy protections in whistleblower cases, and making other miscellaneous and conforming changes.</li>
                                       <li><a href="{press_releases_docs["061711.pdf"].file.url}" target="_blank" title="Press Release">06/17/11</a> - The Tax Court has added to its Internet Web site an “Orders” tab containing two new features to assist the public in identifying and locating orders issued by the Court: Today’s Designated Orders and Orders Search.</li>
                                       <li><a href="{press_releases_docs["050511.pdf"].file.url}" target="_blank" title="Press Release">05/05/11</a> - The Tax Court has adopted amendments to its Rules of Practice and Procedure affecting time periods for filing summary judgment motions, Rule 155 computations, and motions regarding elections to proceed under the small tax case procedure, as well as other amendments to Rules and forms.</li>
                                       <li><a href="{press_releases_docs["031811.pdf"].file.url}" target="_blank" title="Press Release">03/18/11</a> - Comments received on proposed amendments to the Tax Court Rules of Practice and Procedure affecting time periods for filing summary judgment motions, Rule 155 computations, motions regarding elections to proceed under the small tax case procedure, and answers in lien and levy cases, as well as other proposed amendments to Rules and forms.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2010",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["122310.pdf"].file.url}" target="_blank" title="Press Release">12/23/10</a> - Chief Judge John O. Colvin announced today that H.R. 5901, relating to appointment of employees of the United States Tax Court, was passed by the United States Senate on December 17 and by the United States House of Representatives on December 22.</li>
                                       <li><a href="{press_releases_docs["122010.pdf"].file.url}" target="_blank" title="Press Release">12/20/10</a> - The Tax Court has announced proposed amendments to its Rules of Practice and Procedure affecting time periods for filing summary judgment motions, Rule 155 computations, motions regarding elections to proceed under the small tax case procedure, and answers in lien and levy cases. It also proposes other amendments to its Rules and forms.</li>
                                       <li><a href="{press_releases_docs["05052010_exam.pdf"].file.url}" target="_blank" title="Press Release">05/05/10</a> - The Tax Court has issued a press release announcing the date and time of the 2010 written exam for admission to practice for applicants other than attorneys at law.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2009",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["112009.pdf"].file.url}" target="_blank" title="Press Release">11/20/09</a> - The Tax Court has adopted an amendment to its Rules of Practice and Procedure authorizing the electronic filing of documents in all Tax Court cases effective January 1, 2010. The Court is also considering a proposal requiring in the near future electronic filing for most parties represented by practitioners admitted to practice before the Court, and has invited comments on the proposed eFiling requirement to be received by the Court by December 21, 2009.</li>
                                      <li><a href="{press_releases_docs["091809.pdf"].file.url}" target="_blank" title="Press Release"> 09/18/09</a> - The Tax Court has adopted amendments to various Rules of Practice and Procedure to conform them more closely with the Federal Rules of Civil Procedure.</li>
                                       <li><a href="{press_releases_docs["032709.pdf"].file.url}" target="_blank" title="Press Release">03/27/09</a> - The Court has proposed amendments to conform its Rules of Practice and Procedure more closely with selected procedures from the Federal Rules of Civil Procedure.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2008",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["100908_Morrison.pdf"].file.url}" target="_blank" title="Press Release">10/09/08</a> - Judge Richard T. Morrison sworn in.</li>
                                       <li><a href="{press_releases_docs["100308.pdf"].file.url}" target="_blank" title="Press Release">10/03/08</a> - The Court has adopted amendments to its Rules of Practice and Procedure regarding whistleblower award actions and electronic service, and other amendments to its Rules and forms.</li>
                                       <li><a href="{press_releases_docs["080408_Gustafson.pdf"].file.url}" target="_blank" title="Press Release">08/04/08</a> - Judge David Gustafson sworn in.</li>
                                       <li><a href="{press_releases_docs["080108_Paris.pdf"].file.url}" target="_blank" title="Press Release">08/01/08</a> - Judge Elizabeth Crewson Paris sworn in.</li>
                                       <li><a href="{press_releases_docs["060208.pdf"].file.url}" target="_blank" title="Press Release">06/02/08</a> - The Court has proposed amendments to its Rules of Practice and Procedure regarding whistleblower award actions and electronic service, and other amendments to its Rules and forms.</li>
                                       <li><a href="{press_releases_docs["043008.pdf"].file.url}" target="_blank" title="Press Release">04/30/08</a> - The Tax Court has issued a press release announcing the date and time of the 2008 written exam for admission to practice for applicants other than attorneys at law.</li>
                                       <li><a href="{press_releases_docs["011508.pdf"].file.url}" target="_blank" title="Press Release">01/15/08</a> - The Court has adopted amendments to its Rules regarding privacy issues and access to its electronic case files, and other amendments to its Rules and forms.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2007",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                       <li><a href="{press_releases_docs["122707.pdf"].file.url}" target="_blank" title="Press Release">12/27/07</a> - The Tax Court has announced that it has published on its web site requirements for Tax Clinics and Student Practice Programs.</li>
                                       <li><a href="{press_releases_docs["112707.pdf"].file.url}" target="_blank" title="Press Release">11/27/07</a> - Announcement regarding Final Status Report.</li>
                                       <li><a href="{press_releases_docs["083007.pdf"].file.url}" target="_blank" title="Press Release">08/30/07</a> - In Memory of Special Trial Judge Carleton D. Powell.</li>
                                       <li><a href="{press_releases_docs["042607.pdf"].file.url}" target="_blank" title="Press Release">04/26/07</a> - The Court has adopted the privately funded seminars disclosure policy established by the Judicial Conference of the United States.</li>
                                      <li><a href="{press_releases_docs["040307.pdf"].file.url}" target="_blank" title="Press Release"> 04/03/07</a> - Amendment to Rule 25(b), Tax Court Rules of Practice and Procedure, adopted.</li>
                                      <li><a href="{press_releases_docs["021607_release.pdf"].file.url}" target="_blank" title="Press Release"> 02/16/07</a> - The Court has proposed amending its Rules of Practice and Procedure to include District of Columbia Emancipation Day, April 16, as a legal holiday for purposes of computing time.</li>
                                       <li><a href="{press_releases_docs["011607.pdf"].file.url}" target="_blank" title="Press Release">01/16/07</a> - The Court has proposed amending its Rules of Practice and Procedure to address privacy issues and public access to its electronic case files and to make miscellaneous and conforming changes.</li>
                                       <li><a href="{press_releases_docs["011207.pdf"].file.url}" target="_blank" title="Press Release">01/12/07</a> - Amendment to Rule 173(b), Tax Court Rules of Practice and Procedure, adopted.</li>
                                       </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2006",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                     <li><a href="{press_releases_docs["112806.pdf"].file.url}" target="_blank" title="Press Release">11/28/06</a> - Comments regarding the proposed amendment to Rule 173(b), Tax Court Rules of Practice and Procedure, received, and effective date of the proposed amendment extended until further notice by the Court.</li>
                                     <li><a href="{press_releases_docs["091206.pdf"].file.url}" target="_blank" title="Press Release">09/12/06</a> - The Court has proposed amending its Rules of Practice and Procedure, requiring the filing of answers by the Commissioner of Internal Revenue in all small tax cases.</li>
                                     <li><a href="{press_releases_docs["050306.pdf"].file.url}" target="_blank" title="Press Release">05/03/06</a> - Written Exam for Admission to Practice Announced.</li>
                                     <li><a href="{press_releases_docs["022806.pdf"].file.url}" target="_blank" title="Press Release">02/28/06</a> - Judge John O. Colvin Elected Chief Judge.</li>
                                     <li><a href="{press_releases_docs["012706.pdf"].file.url}" target="_blank" title="Press Release">01/27/06</a> - The installation of a new telephone system necessitates changes to the Court's telephone numbers.</li>
                                     </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2005",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                      <li><a href="{press_releases_docs["121205_electronic_filing.pdf"].file.url}" target="_blank" title="Press Release">12/12/05</a> - The Court has proposed amending its Rules of Practice and Procedure by issuing an Interim Rule and Interim Procedures regarding the establishment of an electronic filing pilot program.</li>
                                      <li><a href="{press_releases_docs["120605.pdf"].file.url}" target="_blank" title="Press Release">12/06/05</a> - The Tax Court will begin accepting credit card payments presented in person at the courthouse and converting checks into electronic funds transfers on December 19, 2005</li>
                                      <li><a href="{press_releases_docs["102005.pdf"].file.url}" target="_blank" title="Press Release">10/20/05</a> - The Court session scheduled to commence on October 24, 2005 in Miami, Florida, has been cancelled until further notice</li>
                                      <li><a href="{press_releases_docs["092105.pdf"].file.url}" target="_blank" title="Press Release">09/21/05</a> - Amendments to Rules of Practice and Procedure Adopted</li>
                                      <li><a href="{press_releases_docs["090105.pdf"].file.url}" target="_blank" title="Press Release">09/01/05</a> - The Court session scheduled for the week of November 14, 2005 in New Orleans, Louisiana, has been cancelled until further notice</li>
                                      <li><a href="{press_releases_docs["070705.pdf"].file.url}" target="_blank" title="Press Release">07/07/05</a> - Proposed Amendments to the Rules of Practice and Procedure announced</li>
                                      <li><a href="{press_releases_docs["062005.pdf"].file.url}" target="_blank" title="Press Release">06/20/05</a> - Robert R. Di Trolio Becomes Clerk of the Court</li>
                                     </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2004",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                     <li><a href="{press_releases_docs["110204.pdf"].file.url}" target="_blank" title="Press Release">11/02/04</a> - Retirement Announcement - Charles S. Casazza, Clerk of the Court</li>
                                     <li><a href="{press_releases_docs["062304.pdf"].file.url}" target="_blank" title="Press Release">06/23/04</a> - Death Announcement - Senior Judge Charles E. Clapp, II</li>
                                     <li><a href="{press_releases_docs["051704_Electronic_Courtroom.pdf"].file.url}" target="_blank" title="Press Release">05/17/04</a> - Availability of Electronic (North) Courtroom announced and guidelines issued</li>
                                     <li><a href="{press_releases_docs["042804.pdf"].file.url}" target="_blank" title="Press Release">04/28/04</a> - Written Exam for Admission to Practice Announced</li>
                                    <li><a href="{press_releases_docs["022304.pdf"].file.url}" target="_blank" title="Press Release"> 02/23/04</a> - Judge Joel Gerber Elected Chief Judge</li>
                                     </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2003",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                      <li><a href="{press_releases_docs["063003_Holmes.pdf"].file.url}" target="_blank" title="Press Release">06/30/03</a> - Judge Mark V. Holmes Sworn In</li>
                                      <li><a href="{press_releases_docs["063003.pdf"].file.url}" target="_blank" title="Press Release">06/30/03</a> - Amendments to Rules of Practice and Procedure Adopted</li>
                                      <li><a href="{press_releases_docs["061703_Kroupa.pdf"].file.url}" target="_blank" title="Press Release">06/17/03</a> - Judge Diane L. Kroupa Sworn In</li>
                                      <li><a href="{press_releases_docs["042803_Wherry.pdf"].file.url}" target="_blank" title="Press Release">04/28/03</a> - Judge Robert A. Wherry, Jr. Sworn In</li>
                                      <li><a href="{press_releases_docs["042203_Goeke.pdf"].file.url}" target="_blank" title="Press Release">04/22/03</a> - Judge Joseph Robert Goeke Sworn In</li>
                                      <li><a href="{press_releases_docs["042203_Haines.pdf"].file.url}" target="_blank" title="Press Release">04/22/03</a> - Judge Harry A. Haines Sworn In</li>
                                      <li><a href="{press_releases_docs["021003.pdf"].file.url}" target="_blank" title="Press Release">02/10/03</a> - Standing Pretrial Order Revised</li>
                                     </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2002",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                     <li><a href="{press_releases_docs["040402.pdf"].file.url}" target="_blank" title="Press Release">04/04/2002</a> - Chief Judge Thomas B. Wells of the United States Tax Court announced that the written examination for admission to practice for applicants other than attorneys at law will be held 11/14/2002</li>
                                     <li><a href="{press_releases_docs["022502.pdf"].file.url}" target="_blank" title="Press Release">02/25/2002</a> - Chief Judge Thomas B Wells has been re-elseced as Cheif Judge of the United States Tax Court for a two year term</li>
                                     <li><a href="{press_releases_docs["011702.pdf"].file.url}" target="_blank" title="Press Release">01/17/2002</a> - Retired Judge Perry Shields of the United States Tax Court died on January 14, 2002, in Knoxville, Tennessee</li>
                                     </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2001",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                     <li><a href="{press_releases_docs["120301.pdf"].file.url}" target="_blank" title="Press Release">12/03/01</a> - Resumption of Delivery of U.S. Mail</li>
                                     <li><a href="{press_releases_docs["110601.pdf"].file.url}" target="_blank" title="Press Release">11/06/01</a> - Delay in Delivery of U.S. Mail</li>
                                     <li><a href="{press_releases_docs["010501.pdf"].file.url}" target="_blank" title="Press Release">01/05/01</a> - Death Announcement - Retired Judge Darrell D. Wiles</li>
                                    <li><a href="{press_releases_docs["010301.pdf"].file.url}" target="_blank" title="Press Release"> 01/03/01</a> - Death Announcement - Retired Judge William Miller Drennen</li>
                                     </ul>""",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "h3",
                        "value": "2000",
                    },
                    {
                        "type": "paragraph",
                        "value": f"""<ul>
                                     <li><a href="{press_releases_docs["042700.pdf"].file.url}" target="_blank" title="Press Release">04/27/00</a> - Written Exam for Admission to Practice Announced</li>
                                     <li><a href="{press_releases_docs["041300.pdf"].file.url}" target="_blank" title="Press Release">04/13/00</a> - Death Announcement - Senior Judge William M. Fay</li>
                                     <li><a href="{press_releases_docs["032000.pdf"].file.url}" target="_blank" title="Press Release">03/20/00</a> - Death announcement - Senior Judge Lawrence A. Wright</li>
                                     <li><a href="{press_releases_docs["022800.pdf"].file.url}" target="_blank" title="Press Release"> 02/28/00</a> - Judge Thomas B. Wells Elected Chief Judge</li>
                                     <li><a href="{press_releases_docs["022300.pdf"].file.url}" target="_blank" title="Press Release"> 02/23/00</a> - Death Announcement - Retired Judge Jules G. Körner III</li>
                                     </ul>""",
                    },
                ],
                show_in_menus=True,
            )
        )
