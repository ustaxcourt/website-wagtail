from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import PressReleasePage
from datetime import datetime

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
    "04072025.pdf": "",
    "05302024.pdf": "",
    "05182020.pdf": "",
    "05172021.pdf": "",
    "05212021.pdf": "",
    "05082023.pdf": "",
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

        for doc_name in list(press_releases_docs.keys()):
            document = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=doc_name,
                title=doc_name,
            )

            if document:
                press_releases_docs[doc_name] = document.id
            else:
                press_releases_docs[doc_name] = None

            press_release_page = PressReleasePage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Press Releases",
                press_release_body=[
                    {
                        "type": "press_releases",
                        "value": [
                            {
                                "release_date": datetime(2025, 4, 7).date(),
                                "details": {
                                    "description": "In Memory of Judge Julian I. Jacobs.",
                                    "file": press_releases_docs["04072025.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2025, 2, 21).date(),
                                "details": {
                                    "description": "The United States Tax Court announced today that Judge Patrick J. Urda has been elected Chief Judge to serve a two-year term beginning June 1, 2025. ",
                                    "file": press_releases_docs["02212025.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2025, 1, 28).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["01282025.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 12, 13).date(),
                                "details": {
                                    "description": "Chief Judge Kathleen Kerrigan announced today that Cathy Fung was sworn in as Judge of the United States Tax Court.",
                                    "file": press_releases_docs["12132024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 10, 22).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["10222024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 10, 16).date(),
                                "details": {
                                    "description": "Chief Judge Kathleen Kerrigan announced today that Rose E. Jenkins was sworn in as Judge of the United States Tax Court.",
                                    "file": press_releases_docs["10162024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 10, 4).date(),
                                "details": {
                                    "description": "Chief Judge Kathleen Kerrigan announced today that Jeffrey S. Arbeit and Benjamin A. Guider III were sworn in as Judges of the United States Tax Court.",
                                    "file": press_releases_docs["10042024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 10, 1).date(),
                                "details": {
                                    "description": "Chief Judge Kerrigan announced the retirement of Judge Joseph H. Gale",
                                    "file": press_releases_docs["10012024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 9, 23).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters",
                                    "file": press_releases_docs["09232024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 8, 8).date(),
                                "details": {
                                    "description": "Chief Judge Kathleen Kerrigan announced today that Kashi Way and Adam B. Landy were sworn in as Judges of the United States Tax Court.",
                                    "file": press_releases_docs["08082024bv2.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 8, 8).date(),
                                "details": {
                                    "description": "Chief Judge Kathleen Kerrigan announced today that the United States Tax Court has adopted final amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["08082024v3.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 5, 30).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters",
                                    "file": press_releases_docs["05302024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 4, 25).date(),
                                "details": {
                                    "description": "Charles Jeane becomes Clerk of the Court.",
                                    "file": press_releases_docs["04252024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 3, 14).date(),
                                "details": {
                                    "description": "In Memory of Judge John O. Colvin.",
                                    "file": press_releases_docs["03142024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 2, 20).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["02202024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 2, 16).date(),
                                "details": {
                                    "description": "The Court announced today that Chief Judge Kathleen Kerrigan has been re-elected and will serve another two-year term beginning June 1, 2024.",
                                    "file": press_releases_docs["02162024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2024, 1, 22).date(),
                                "details": {
                                    "description": "Chief Judge Kathleen Kerrigan announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["01222024.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2023, 11, 28).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["11282023.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2023, 8, 28).date(),
                                "details": {
                                    "description": "Chief Judge Kathleen Kerrigan announced that Jennifer E. Siegel and Zachary S. Fried have been selected to serve as Special Trial Judges of the United States Tax Court.",
                                    "file": press_releases_docs["08282023.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2023, 8, 4).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["08042023.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2023, 5, 8).date(),
                                "details": {
                                    "description": "The U.S. Tax Court announced that the written examination for applicants other than attorneys at law (nonattorney applicants) for admission to practice before the U.S. Tax Court will be held remotely at 12:30pm EST on Wednesday, November 8, 2023, using the ExamSoft platform.",
                                    "file": press_releases_docs["05082023.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2023, 3, 20).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["03202023.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2023, 3, 20).date(),
                                "details": {
                                    "description": "Chief Judge Kathleen Kerrigan announced today that the United States Tax Court has adopted final amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["08042023.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 12, 16).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["12162022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 11, 21).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["11212022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 10, 26).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["10262022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 10, 14).date(),
                                "details": {
                                    "description": "In Memory of Judge Herbert Chabot.",
                                    "file": press_releases_docs["10142022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 8, 25).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["08252022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 8, 23).date(),
                                "details": {
                                    "description": "The U.S. Tax Court has issued Administrative Order 2022-01, which repeals Administrative Orders 2021-02 and 2021-03, effective August 29, 2022.",
                                    "file": press_releases_docs["08232022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 6, 24).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["06242022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 6, 3).date(),
                                "details": {
                                    "description": "Beginning June 6, 2022, the Tax Court’s Washington, D.C. courthouse will be open to the public.",
                                    "file": press_releases_docs["06032022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 4, 1).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced today that, effective March 31, 2022, Special Trial Judge Daniel A. Guy, Jr. has retired.",
                                    "file": press_releases_docs["04012022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 3, 23).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["03232022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 3, 8).date(),
                                "details": {
                                    "description": "In Memory of Judge Joel Gerber",
                                    "file": press_releases_docs["03082022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 2, 25).date(),
                                "details": {
                                    "description": "The United States Tax Court announced today that Judge Kathleen Kerrigan has been elected Chief Judge to serve a two-year term beginning June 1, 2022.",
                                    "file": press_releases_docs["02252022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 2, 18).date(),
                                "details": {
                                    "description": "In Memory of Judge Robert P. Ruwe",
                                    "file": press_releases_docs["02182022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 2, 2).date(),
                                "details": {
                                    "description": "Since December 28, 2020, over 750 new features have been added to DAWSON, the Tax Court’s case-management system.",
                                    "file": press_releases_docs["02012022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 1, 26).date(),
                                "details": {
                                    "description": "After assessing public health and other factors relating to nationwide COVID-19 cases, the U.S. Tax Court has determined that it is not appropriate to conduct in-person proceedings through February 25, 2022.",
                                    "file": press_releases_docs["01262022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 1, 24).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["01242022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2022, 1, 12).date(),
                                "details": {
                                    "description": "After assessing public health and other factors relating to the rapid nationwide increase of COVID-19 cases, the U.S. Tax Court has determined that it is not appropriate to conduct in-person proceedings in January 2022.",
                                    "file": press_releases_docs["01122022.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 12, 28).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced today that opinion search is now available in the DAWSON case management system.",
                                    "file": press_releases_docs["12282021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 12, 14).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced today that order search is now available in the DAWSON case management system.",
                                    "file": press_releases_docs["12142021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 12, 9).date(),
                                "details": {
                                    "description": "From January 1, 2021, through November 30, 2021, the Court received 33,300 petitions.",
                                    "file": press_releases_docs["12092021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 12, 6).date(),
                                "details": {
                                    "description": "On December 6, 2021, Chief Judge Maurice B. Foley announced that Adam B. Landy and Eunkyong Choi have each been selected to serve as a Special Trial Judge and taken the oath of office.",
                                    "file": press_releases_docs["12062021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 11, 19).date(),
                                "details": {
                                    "description": "On November 18, 2021, Special Trial Judge Daniel A. Guy, Jr. received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.",
                                    "file": press_releases_docs["11192021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 10, 14).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["10142021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 10, 5).date(),
                                "details": {
                                    "description": "To provide guidance with respect to in-person proceedings, the Court has posted a new publication, Court Standards and Protocols to Protect Public Health, as well as issued Administrative Order 2021-02, Washington, D.C. Courthouse Access.",
                                    "file": press_releases_docs["10052021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 8, 27).date(),
                                "details": {
                                    "description": "On August 27, 2021, the Court issued Administrative Order 2021-01, Policies for Remote (Virtual) Proceedings, which outlines the policies adopted allowing for both in-person and remote (virtual) trials.",
                                    "file": press_releases_docs["08272021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 8, 16).date(),
                                "details": {
                                    "description": "The Court met with various stakeholders to address concerns relating to the increased number of petitions being filed and to limit the potential for premature assessment and enforcement action.",
                                    "file": press_releases_docs["08162021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 7, 23).date(),
                                "details": {
                                    "description": "The United States Tax Court has received a significantly higher number of petitions this year. The Court is processing petitions expeditiously, but the increased volume has caused a delay between when a petition is received by the Court and when it is served on the Internal Revenue Service.",
                                    "file": press_releases_docs["07232021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 5, 21).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["05212021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 5, 17).date(),
                                "details": {
                                    "description": "The United States Tax Court announced today that the examination for admission to practice before the Court will be held remotely on Wednesday, November 17, 2021.",
                                    "file": press_releases_docs["05172021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 4, 5).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced today that the United States Tax Court will begin accepting applications for its new Diversity in Government Internship Program (DiG Tax).",
                                    "file": press_releases_docs["04052021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 2, 23).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["02232021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 2, 12).date(),
                                "details": {
                                    "description": "The Tax Court announces its Diversity & Inclusion Series. The series is comprised of webinars that will spotlight different trailblazers and their paths to, and success in, the field of tax law.",
                                    "file": press_releases_docs["02122021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2021, 1, 11).date(),
                                "details": {
                                    "description": """Chief Judge Maurice B. Foley announced today that DAWSON has been updated to include “Today’s Orders”.""",
                                    "file": press_releases_docs["01112021.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 12, 18).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced today that on December 28, 2020, the United States Tax Court will officially launch DAWSON (Docket Access Within a Secure Online Network), its new case management system.",
                                    "file": press_releases_docs["12182020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 12, 10).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced today that the Court has updated its guidance on procedures related to subpoenas for remote proceedings.",
                                    "file": press_releases_docs["12102020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 11, 30).date(),
                                "details": {
                                    "description": "Senior Judge Robert P. Ruwe has fully retired and is no longer recalled for judicial service.",
                                    "file": press_releases_docs["11302020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 11, 20).date(),
                                "details": {
                                    "description": "For paper documents requiring multiple signatures and postmarked November 21, 2020 through December 28, 2020, the Court has modified its signature requirements as outlined in Administrative Order 2020-05.",
                                    "file": press_releases_docs["11202020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 11, 16).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["11162020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 11, 12).date(),
                                "details": {
                                    "description": "Beginning Monday, November 16, 2020, the Court will resume accepting hand-delivered documents to the main courthouse building.",
                                    "file": press_releases_docs["11122020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 10, 29).date(),
                                "details": {
                                    "description": "Effective Friday, October 30, 2020, and until further notice, the United States Tax Court will be suspending its in-person acceptance of hand-delivered documents.",
                                    "file": press_releases_docs["10292020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 10, 7).date(),
                                "details": {
                                    "description": "To facilitate the transition to the Court's new case management system, beginning at 5:00 PM Eastern Time on November 20, 2020, the current e-filing system will become inaccessible and all electronic files will become read-only.",
                                    "file": press_releases_docs["10072020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 9, 9).date(),
                                "details": {
                                    "description": "Chief Special Trial Judge Lewis R. Carluzzo received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.",
                                    "file": press_releases_docs["09092020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 8, 17).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["08172020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 8, 6).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced additional guidance with respect to remote proceedings.",
                                    "file": press_releases_docs["08062020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 7, 20).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["07202020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 7, 17).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced that, effective July 16, 2020, Senior Judge Joel Gerber has retired and is no longer recalled for judicial service.",
                                    "file": press_releases_docs["07172020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 6, 24).date(),
                                "details": {
                                    "description": "Beginning July 10, 2020, the Clerk’s Office will accept hand-delivered documents between the hours of 8:00 AM and 4:30 PM, Monday through Friday.",
                                    "file": press_releases_docs["06242020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 6, 22).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["06222020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 6, 19).date(),
                                "details": {
                                    "description": "Mail delivery will resume on July 10, 2020.",
                                    "file": press_releases_docs["06192020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 5, 29).date(),
                                "details": {
                                    "description": "To accommodate continuing uncertainties relating to the COVID-19 pandemic, and until further notice, Court proceedings will be conducted remotely.",
                                    "file": press_releases_docs[
                                        "05292020_proceedings.pdf"
                                    ],
                                },
                            },
                            {
                                "release_date": datetime(2020, 5, 29).date(),
                                "details": {
                                    "description": "The Court will resume accepting requests for photocopies of Court records from non- parties (copy requests) on June 1, 2020.",
                                    "file": press_releases_docs[
                                        "05292020_copywork.pdf"
                                    ],
                                },
                            },
                            {
                                "release_date": datetime(2020, 5, 18).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["05182020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 5, 7).date(),
                                "details": {
                                    "description": "To mitigate risks and concerns related to COVID-19, the Court is postponing the November 2020 nonattorney examination to the fall of 2021.",
                                    "file": press_releases_docs["05072020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 5, 4).date(),
                                "details": {
                                    "description": "The Court announced that attorney applications for admission to practice before the Court may be emailed to the Admissions Office.",
                                    "file": press_releases_docs["05042020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 4, 21).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["04212020_1.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 4, 21).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["04212020_2.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 3, 23).date(),
                                "details": {
                                    "description": "The United States Tax Court building remains closed and trial sessions through June 30, 2020 are canceled.",
                                    "file": press_releases_docs["03232020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 3, 18).date(),
                                "details": {
                                    "description": "The Court announced that effective as of 9:00 PM on March 18, 2020, and until further notice, the United States Tax Court building is closed.",
                                    "file": press_releases_docs["03182020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 3, 13).date(),
                                "details": {
                                    "description": "The Court has determined that it is appropriate to cancel certain trial sessions and to close the Court to visitors, effective immediately.",
                                    "file": press_releases_docs["03132020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 3, 11).date(),
                                "details": {
                                    "description": "The Court has determined that it is appropriate to cancel certain trial sessions.",
                                    "file": press_releases_docs["03112020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 2, 24).date(),
                                "details": {
                                    "description": "The Court announced that Chief Judge Maurice B. Foley has been re-elected and will serve another two-year term beginning June 1, 2020.",
                                    "file": press_releases_docs["02242020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 2, 21).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["02212020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2020, 1, 15).date(),
                                "details": {
                                    "description": "The Tax Court has adopted amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["01152020.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 11, 25).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["112519.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 11, 22).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["112219.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 9, 23).date(),
                                "details": {
                                    "description": "In Memory of Judge Arthur L. Nims III.",
                                    "file": press_releases_docs["092319.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 9, 4).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced the retirement of Special Trial Judge Robert N. Armen, Jr.",
                                    "file": press_releases_docs["090419.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 7, 15).date(),
                                "details": {
                                    "description": "The Tax Court has adopted amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["071519.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 7, 12).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["071219.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 6, 11).date(),
                                "details": {
                                    "description": "On June 11, 2019, Chief Judge Maurice B. Foley announced that, effective as of June 7, 2019, Senior Judge Julian I. Jacobs has fully retired and is no longer recalled for judicial service.",
                                    "file": press_releases_docs["061119.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 5, 17).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["051719.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 5, 10).date(),
                                "details": {
                                    "description": "The Court issued Administrative Order No. 2019-01, outlining procedures for filing limited entries of appearance in Tax Court cases.",
                                    "file": press_releases_docs["051019.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 4, 26).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["051019.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 3, 15).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["031519.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 2, 4).date(),
                                "details": {
                                    "description": "The Tax Court has extended the period for submission of comments regarding interim and proposed partnership rules.",
                                    "file": press_releases_docs["020419.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2019, 1, 26).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced the resumption of full operations of the United States Tax Court effective Monday, January 28, 2019.",
                                    "file": press_releases_docs["012619.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 12, 19).date(),
                                "details": {
                                    "description": "The Tax Court has announced interim and proposed amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["121918.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 11, 30).date(),
                                "details": {
                                    "description": "The Tax Court has adopted amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["113018.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 11, 30).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs[
                                        "113018_disciplinary_matters.pdf"
                                    ],
                                },
                            },
                            {
                                "release_date": datetime(2018, 10, 12).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["101218.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 9, 25).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["092518.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 9, 24).date(),
                                "details": {
                                    "description": "Chief Judge Maurice B. Foley announced the retirement of Judge Carolyn P. Chiechi.",
                                    "file": press_releases_docs["092418.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 9, 6).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["090618.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 7, 20).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["072018.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 5, 8).date(),
                                "details": {
                                    "description": "The Tax Court has issued a press release announcing the date and time of the 2018 written exam for admission to practice for applicants other than attorneys at law.",
                                    "file": press_releases_docs["050818.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 4, 19).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["041918.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 2, 26).date(),
                                "details": {
                                    "description": "Judge Maurice B. Foley will become Chief Judge June 1, 2018.",
                                    "file": press_releases_docs["022618.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2018, 1, 3).date(),
                                "details": {
                                    "description": "Chief Judge L. Paige Marvel announced the retirement of Judge Robert A. Wherry, Jr.",
                                    "file": press_releases_docs["010318.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2017, 12, 21).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["122117.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2017, 12, 21).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["122117.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2017, 10, 13).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["101317.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2017, 9, 15).date(),
                                "details": {
                                    "description": "The 2018 Tax Court Judicial Conference will be held in Chicago, Illinois, on the campus of Northwestern University’s Pritzker School of Law in March.",
                                    "file": press_releases_docs["091517.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2017, 8, 31).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["083117.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2017, 5, 12).date(),
                                "details": {
                                    "description": "The Tax Court announced that Chief Special Trial Judge Peter J. Panuthos has decided to step down as Chief Special Trial Judge, effective September 1, 2017, and that Special Trial Judge Lewis R. Carluzzo has been named Chief Special Trial Judge, effective September 1, 2017.",
                                    "file": press_releases_docs["051217.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2017, 4, 13).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["041317.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2017, 2, 17).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["021717.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 12, 16).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["121616.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 10, 12).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["101216.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 7, 18).date(),
                                "details": {
                                    "description": "Chief Judge L. Paige Marvel has released a statement acknowledging the passing on July 15, 2016, of the Honorable Howard A. Dawson, Jr., the longest-serving judge in Tax Court history.",
                                    "file": press_releases_docs["071816.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 6, 14).date(),
                                "details": {
                                    "description": "The Chief Judge has announced the adoption of Rules for Judicial Conduct and Disability Proceedings for the United States Tax Court.",
                                    "file": press_releases_docs["061416.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 5, 31).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["053116.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 5, 6).date(),
                                "details": {
                                    "description": "The Tax Court has issued a press release announcing the date and time of the 2016 written exam for admission to practice for applicants other than attorneys at law.",
                                    "file": press_releases_docs["050616.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 3, 28).date(),
                                "details": {
                                    "description": "The Tax Court has announced interim and proposed amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["032816.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 3, 24).date(),
                                "details": {
                                    "description": "Diana L. Leyden to be sworn in as a Special Trial Judge.",
                                    "file": press_releases_docs["032416.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 2, 29).date(),
                                "details": {
                                    "description": "Judge L. Paige Marvel will become Chief Judge June 1, 2016.",
                                    "file": press_releases_docs["022916.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 2, 19).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["021916.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2016, 1, 11).date(),
                                "details": {
                                    "description": "The Tax Court has announced proposed amendments to its Rules of Practice and Procedure.",
                                    "file": press_releases_docs["011116.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2015, 12, 18).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["121815.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2015, 10, 15).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["101515.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2015, 8, 6).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["080615.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2015, 7, 1).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["070115.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2015, 5, 29).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["052915.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2015, 4, 24).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["042415.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2015, 2, 24).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["022415.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2014, 12, 19).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["121914.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2014, 11, 14).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["111414.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2014, 10, 10).date(),
                                "details": {
                                    "description": "The Court issued a press release in Amazon.Com, Inc. & Subsidiaries v. Commissioner of Internal Revenue.",
                                    "file": press_releases_docs["101014.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2014, 9, 5).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["090514.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2014, 7, 18).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["071814.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2014, 5, 13).date(),
                                "details": {
                                    "description": "The Tax Court has issued a press release announcing the date and time of the 2014 written exam for admission to practice for applicants other than attorneys at law.",
                                    "file": press_releases_docs["051314.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2014, 4, 25).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["042514.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2013, 12, 20).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["122013.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2013, 9, 30).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["093013.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2013, 6, 25).date(),
                                "details": {
                                    "description": "Tax Court Disciplinary Matters.",
                                    "file": press_releases_docs["062513.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 9, 18).date(),
                                "details": {
                                    "description": "In Memory of Judge Russell E. Train.",
                                    "file": press_releases_docs["091812.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 9, 11).date(),
                                "details": {
                                    "description": "In Memory of Judge Lapsley W. Hamblen, Jr.",
                                    "file": press_releases_docs["091112.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 7, 13).date(),
                                "details": {
                                    "description": "In Memory of Judge Renato Beghe.",
                                    "file": press_releases_docs["071312.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 7, 6).date(),
                                "details": {
                                    "description": "The Tax Court has adopted amendments to its Rules of Practice and Procedure requiring electronic filing by most practitioners, providing privacy protections in whistleblower cases, and making other miscellaneous and conforming changes.",
                                    "file": press_releases_docs["070612.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 6, 26).date(),
                                "details": {
                                    "description": "The Tax Court announces a uniform method of spot-citing Memorandum Opinions.",
                                    "file": press_releases_docs["062612.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 6, 12).date(),
                                "details": {
                                    "description": "The Tax Court announces the investiture of Judge Kathleen Kerrigan.",
                                    "file": press_releases_docs["061212.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 5, 8).date(),
                                "details": {
                                    "description": "The Tax Court has issued a press release announcing the date and time of the 2012 written exam for admission to practice for applicants other than attorneys at law.",
                                    "file": press_releases_docs["050812.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 5, 7).date(),
                                "details": {
                                    "description": "Judge Michael B. Thornton has been elected as Chief Judge of the United States Tax Court to serve a 2-year term beginning June 1, 2012.",
                                    "file": press_releases_docs["050712.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 4, 30).date(),
                                "details": {
                                    "description": "Judge Robert P. Ruwe received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.",
                                    "file": press_releases_docs["043012.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 4, 17).date(),
                                "details": {
                                    "description": "Daniel A. Guy, Jr., will take the oath of office to serve as a Special Trial Judge of the United States Tax Court on May 31, 2012.",
                                    "file": press_releases_docs["041712.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 3, 26).date(),
                                "details": {
                                    "description": "Chief Special Trial Judge Peter J. Panuthos received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.",
                                    "file": press_releases_docs["032612.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2012, 3, 6).date(),
                                "details": {
                                    "description": "Comments received on proposed amendments to the Tax Court Rules of Practice and Procedure requiring electronic filing by most parties represented by counsel, providing privacy protections in whistleblower cases, and making other miscellaneous and conforming changes.",
                                    "file": press_releases_docs["030612.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2011, 12, 28).date(),
                                "details": {
                                    "description": "The Tax Court has announced proposed amendments to its Rules of Practice and Procedure reducing the number of copies required for papers filed with the Court, requiring electronic filing by most parties represented by counsel, providing privacy protections in whistleblower cases, and making other miscellaneous and conforming changes.",
                                    "file": press_releases_docs["122811.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2011, 6, 17).date(),
                                "details": {
                                    "description": "The Tax Court has added to its Internet Web site an “Orders” tab containing two new features to assist the public in identifying and locating orders issued by the Court: Today’s Designated Orders and Orders Search.",
                                    "file": press_releases_docs["061711.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2011, 5, 5).date(),
                                "details": {
                                    "description": "The Tax Court has adopted amendments to its Rules of Practice and Procedure affecting time periods for filing summary judgment motions, Rule 155 computations, and motions regarding elections to proceed under the small tax case procedure, as well as other amendments to Rules and forms.",
                                    "file": press_releases_docs["050511.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2011, 3, 18).date(),
                                "details": {
                                    "description": "Comments received on proposed amendments to the Tax Court Rules of Practice and Procedure affecting time periods for filing summary judgment motions, Rule 155 computations, motions regarding elections to proceed under the small tax case procedure, and answers in lien and levy cases, as well as other proposed amendments to Rules and forms.",
                                    "file": press_releases_docs["031811.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2010, 12, 23).date(),
                                "details": {
                                    "description": "Chief Judge John O. Colvin announced today that H.R. 5901, relating to appointment of employees of the United States Tax Court, was passed by the United States Senate on December 17 and by the United States House of Representatives on December 22.",
                                    "file": press_releases_docs["122310.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2010, 12, 20).date(),
                                "details": {
                                    "description": "The Tax Court has announced proposed amendments to its Rules of Practice and Procedure affecting time periods for filing summary judgment motions, Rule 155 computations, motions regarding elections to proceed under the small tax case procedure, and answers in lien and levy cases. It also proposes other amendments to its Rules and forms.",
                                    "file": press_releases_docs["122010.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2010, 5, 5).date(),
                                "details": {
                                    "description": "The Tax Court has issued a press release announcing the date and time of the 2010 written exam for admission to practice for applicants other than attorneys at law.",
                                    "file": press_releases_docs["05052010_exam.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2009, 11, 20).date(),
                                "details": {
                                    "description": "The Tax Court has adopted an amendment to its Rules of Practice and Procedure authorizing the electronic filing of documents in all Tax Court cases effective January 1, 2010. The Court is also considering a proposal requiring in the near future electronic filing for most parties represented by practitioners admitted to practice before the Court, and has invited comments on the proposed eFiling requirement to be received by the Court by December 21, 2009.",
                                    "file": press_releases_docs["112009.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2009, 9, 18).date(),
                                "details": {
                                    "description": "The Tax Court has adopted amendments to various Rules of Practice and Procedure to conform them more closely with the Federal Rules of Civil Procedure.",
                                    "file": press_releases_docs["091809.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2009, 3, 27).date(),
                                "details": {
                                    "description": "The Court has proposed amendments to conform its Rules of Practice and Procedure more closely with selected procedures from the Federal Rules of Civil Procedure.",
                                    "file": press_releases_docs["032709.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2008, 10, 9).date(),
                                "details": {
                                    "description": "Judge Richard T. Morrison sworn in.",
                                    "file": press_releases_docs["100908_Morrison.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2008, 10, 9).date(),
                                "details": {
                                    "description": "Judge Richard T. Morrison sworn in.",
                                    "file": press_releases_docs["100908_Morrison.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2008, 10, 3).date(),
                                "details": {
                                    "description": "The Court has adopted amendments to its Rules of Practice and Procedure regarding whistleblower award actions and electronic service, and other amendments to its Rules and forms.",
                                    "file": press_releases_docs["100908_Morrison.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2008, 8, 4).date(),
                                "details": {
                                    "description": "Judge David Gustafson sworn in.",
                                    "file": press_releases_docs["080408_Gustafson.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2008, 8, 1).date(),
                                "details": {
                                    "description": "Judge Elizabeth Crewson Paris sworn in.",
                                    "file": press_releases_docs["080408_Gustafson.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2008, 6, 2).date(),
                                "details": {
                                    "description": "The Court has proposed amendments to its Rules of Practice and Procedure regarding whistleblower award actions and electronic service, and other amendments to its Rules and forms.",
                                    "file": press_releases_docs["060208.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2008, 4, 30).date(),
                                "details": {
                                    "description": "The Tax Court has issued a press release announcing the date and time of the 2008 written exam for admission to practice for applicants other than attorneys at law.",
                                    "file": press_releases_docs["043008.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2008, 4, 30).date(),
                                "details": {
                                    "description": "The Tax Court has issued a press release announcing the date and time of the 2008 written exam for admission to practice for applicants other than attorneys at law.",
                                    "file": press_releases_docs["043008.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2008, 1, 15).date(),
                                "details": {
                                    "description": "The Court has adopted amendments to its Rules regarding privacy issues and access to its electronic case files, and other amendments to its Rules and forms.",
                                    "file": press_releases_docs["011508.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 12, 27).date(),
                                "details": {
                                    "description": "The Tax Court has announced that it has published on its web site requirements for Tax Clinics and Student Practice Programs.",
                                    "file": press_releases_docs["011508.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 11, 27).date(),
                                "details": {
                                    "description": "Announcement regarding Final Status Report.",
                                    "file": press_releases_docs["112707.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 8, 30).date(),
                                "details": {
                                    "description": "In Memory of Special Trial Judge Carleton D. Powell.",
                                    "file": press_releases_docs["083007.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 8, 30).date(),
                                "details": {
                                    "description": "Announcement regarding Final Status Report.",
                                    "file": press_releases_docs["083007.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 4, 26).date(),
                                "details": {
                                    "description": "Announcement regarding Final Status Report.",
                                    "file": press_releases_docs["042607.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 4, 26).date(),
                                "details": {
                                    "description": "The Court has adopted the privately funded seminars disclosure policy established by the Judicial Conference of the United States.",
                                    "file": press_releases_docs["042607.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 4, 3).date(),
                                "details": {
                                    "description": "Amendment to Rule 25(b), Tax Court Rules of Practice and Procedure, adopted.",
                                    "file": press_releases_docs["040307.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 2, 16).date(),
                                "details": {
                                    "description": "The Court has proposed amending its Rules of Practice and Procedure to include District of Columbia Emancipation Day, April 16, as a legal holiday for purposes of computing time.",
                                    "file": press_releases_docs["021607_release.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 1, 16).date(),
                                "details": {
                                    "description": "The Court has proposed amending its Rules of Practice and Procedure to address privacy issues and public access to its electronic case files and to make miscellaneous and conforming changes.",
                                    "file": press_releases_docs["011607.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2007, 1, 12).date(),
                                "details": {
                                    "description": "Amendment to Rule 173(b), Tax Court Rules of Practice and Procedure, adopted.",
                                    "file": press_releases_docs["011207.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2006, 11, 28).date(),
                                "details": {
                                    "description": "Comments regarding the proposed amendment to Rule 173(b), Tax Court Rules of Practice and Procedure, received, and effective date of the proposed amendment extended until further notice by the Court.",
                                    "file": press_releases_docs["112806.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2006, 9, 12).date(),
                                "details": {
                                    "description": "The Court has proposed amending its Rules of Practice and Procedure, requiring the filing of answers by the Commissioner of Internal Revenue in all small tax cases.",
                                    "file": press_releases_docs["091206.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2006, 5, 3).date(),
                                "details": {
                                    "description": "Written Exam for Admission to Practice Announced.",
                                    "file": press_releases_docs["050306.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2006, 2, 28).date(),
                                "details": {
                                    "description": "Judge John O. Colvin Elected Chief Judge.",
                                    "file": press_releases_docs["022806.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2006, 1, 27).date(),
                                "details": {
                                    "description": "The installation of a new telephone system necessitates changes to the Court's telephone numbers.",
                                    "file": press_releases_docs["012706.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2005, 12, 12).date(),
                                "details": {
                                    "description": "The Court has proposed amending its Rules of Practice and Procedure by issuing an Interim Rule and Interim Procedures regarding the establishment of an electronic filing pilot program.",
                                    "file": press_releases_docs[
                                        "121205_electronic_filing.pdf"
                                    ],
                                },
                            },
                            {
                                "release_date": datetime(2005, 12, 6).date(),
                                "details": {
                                    "description": "The Tax Court will begin accepting credit card payments presented in person at the courthouse and converting checks into electronic funds transfers on December 19, 2005",
                                    "file": press_releases_docs["120605.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2005, 10, 20).date(),
                                "details": {
                                    "description": "The Court session scheduled to commence on October 24, 2005 in Miami, Florida, has been cancelled until further notice",
                                    "file": press_releases_docs["102005.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2005, 9, 21).date(),
                                "details": {
                                    "description": "Amendments to Rules of Practice and Procedure Adopted",
                                    "file": press_releases_docs["092105.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2005, 9, 1).date(),
                                "details": {
                                    "description": "The Court session scheduled for the week of November 14, 2005 in New Orleans, Louisiana, has been cancelled until further notice",
                                    "file": press_releases_docs["090105.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2005, 7, 7).date(),
                                "details": {
                                    "description": "Proposed Amendments to the Rules of Practice and Procedure announced",
                                    "file": press_releases_docs["070705.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2005, 6, 20).date(),
                                "details": {
                                    "description": "Robert R. Di Trolio Becomes Clerk of the Court",
                                    "file": press_releases_docs["062005.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2004, 11, 2).date(),
                                "details": {
                                    "description": "Retirement Announcement - Charles S. Casazza, Clerk of the Court",
                                    "file": press_releases_docs["110204.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2004, 6, 23).date(),
                                "details": {
                                    "description": "Death Announcement - Senior Judge Charles E. Clapp, II",
                                    "file": press_releases_docs["062304.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2004, 5, 17).date(),
                                "details": {
                                    "description": "Availability of Electronic (North) Courtroom announced and guidelines issued",
                                    "file": press_releases_docs[
                                        "051704_Electronic_Courtroom.pdf"
                                    ],
                                },
                            },
                            {
                                "release_date": datetime(2004, 4, 28).date(),
                                "details": {
                                    "description": "Written Exam for Admission to Practice Announced",
                                    "file": press_releases_docs[
                                        "051704_Electronic_Courtroom.pdf"
                                    ],
                                },
                            },
                            {
                                "release_date": datetime(2004, 2, 23).date(),
                                "details": {
                                    "description": "Judge Joel Gerber Elected Chief Judge",
                                    "file": press_releases_docs["022304.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2003, 6, 30).date(),
                                "details": {
                                    "description": "Judge Mark V. Holmes Sworn In",
                                    "file": press_releases_docs["063003_Holmes.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2003, 6, 30).date(),
                                "details": {
                                    "description": "Amendments to Rules of Practice and Procedure Adopted",
                                    "file": press_releases_docs["063003.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2003, 6, 17).date(),
                                "details": {
                                    "description": "Judge Diane L. Kroupa Sworn In",
                                    "file": press_releases_docs["061703_Kroupa.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2003, 4, 28).date(),
                                "details": {
                                    "description": "Judge Robert A. Wherry, Jr. Sworn In",
                                    "file": press_releases_docs["042803_Wherry.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2003, 4, 22).date(),
                                "details": {
                                    "description": "Judge Robert A. Wherry, Jr. Sworn In",
                                    "file": press_releases_docs["042203_Goeke.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2003, 4, 22).date(),
                                "details": {
                                    "description": "Judge Joseph Robert Goeke Sworn In",
                                    "file": press_releases_docs["042203_Haines.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2003, 2, 10).date(),
                                "details": {
                                    "description": "Standing Pretrial Order Revised",
                                    "file": press_releases_docs["021003.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2002, 4, 4).date(),
                                "details": {
                                    "description": "Chief Judge Thomas B. Wells of the United States Tax Court announced that the written examination for admission to practice for applicants other than attorneys at law will be held 11/14/2002",
                                    "file": press_releases_docs["040402.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2002, 2, 25).date(),
                                "details": {
                                    "description": "Chief Judge Thomas B Wells has been re-elseced as Cheif Judge of the United States Tax Court for a two year term",
                                    "file": press_releases_docs["022502.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2002, 1, 17).date(),
                                "details": {
                                    "description": "Retired Judge Perry Shields of the United States Tax Court died on January 14, 2002, in Knoxville, Tennessee",
                                    "file": press_releases_docs["011702.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2001, 12, 3).date(),
                                "details": {
                                    "description": "Resumption of Delivery of U.S. Mail",
                                    "file": press_releases_docs["120301.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2001, 1, 5).date(),
                                "details": {
                                    "description": "Death Announcement - Retired Judge Darrell D. Wiles",
                                    "file": press_releases_docs["010501.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2001, 1, 3).date(),
                                "details": {
                                    "description": "Death Announcement - Retired Judge William Miller Drennen",
                                    "file": press_releases_docs["010301.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2000, 4, 27).date(),
                                "details": {
                                    "description": "Written Exam for Admission to Practice Announced",
                                    "file": press_releases_docs["042700.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2000, 4, 13).date(),
                                "details": {
                                    "description": "Death Announcement - Senior Judge William M. Fay",
                                    "file": press_releases_docs["041300.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2000, 3, 20).date(),
                                "details": {
                                    "description": "Death announcement - Senior Judge Lawrence A. Wright",
                                    "file": press_releases_docs["032000.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2000, 2, 28).date(),
                                "details": {
                                    "description": "Judge Thomas B. Wells Elected Chief Judge",
                                    "file": press_releases_docs["022800.pdf"],
                                },
                            },
                            {
                                "release_date": datetime(2000, 2, 28).date(),
                                "details": {
                                    "description": "Death Announcement - Retired Judge Jules G. Körner III",
                                    "file": press_releases_docs["022800.pdf"],
                                },
                            },
                        ],
                    },
                ],
                show_in_menus=True,
            )

        home_page.add_child(instance=press_release_page)
        press_release_page.save_revision().publish()
        self.logger.write(f"'{title}' page created and published.")
