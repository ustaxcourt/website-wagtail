from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from wagtail.models import Page

from home.management.commands.pages.page_initializer import PageInitializer
from home.models import PressReleasePage
from home.models.snippets.news_item import NewsItem
from home.models.utils.execute_script import ExecuteScript

import logging

logger = logging.getLogger(__name__)

# One-time seed data: historical press releases, ported directly to NewsItem
# snippets. Each tuple is (year, month, day, description, source document
# filename under PageInitializer.DOCUMENTS_BASE_PATH).
PRESS_RELEASE_NEWS_ITEMS = [
    (
        2025,
        4,
        16,
        "The Tax Court announced that Chief Special Trial Judge Lewis R. Carluzzo has decided to step down as Chief Special Trial Judge, effective May 2, 2025, and that Special Trial Judge Zachary S. Fried has been named Chief Special Trial Judge, effective May 3, 2025.",
        "04162025.pdf",
    ),
    (2025, 4, 7, "In Memory of Judge Julian I. Jacobs.", "04072025.pdf"),
    (
        2025,
        2,
        21,
        "The United States Tax Court announced today that Judge Patrick J. Urda has been elected Chief Judge to serve a two-year term beginning June 1, 2025. ",
        "02212025.pdf",
    ),
    (2025, 1, 28, "Tax Court Disciplinary Matters.", "01282025.pdf"),
    (
        2024,
        12,
        13,
        "Chief Judge Kathleen Kerrigan announced today that Cathy Fung was sworn in as Judge of the United States Tax Court.",
        "12132024.pdf",
    ),
    (2024, 10, 22, "Tax Court Disciplinary Matters.", "10222024.pdf"),
    (
        2024,
        10,
        16,
        "Chief Judge Kathleen Kerrigan announced today that Rose E. Jenkins was sworn in as Judge of the United States Tax Court.",
        "10162024.pdf",
    ),
    (
        2024,
        10,
        4,
        "Chief Judge Kathleen Kerrigan announced today that Jeffrey S. Arbeit and Benjamin A. Guider III were sworn in as Judges of the United States Tax Court.",
        "10042024.pdf",
    ),
    (
        2024,
        10,
        1,
        "Chief Judge Kerrigan announced the retirement of Judge Joseph H. Gale",
        "10012024.pdf",
    ),
    (2024, 9, 23, "Tax Court Disciplinary Matters", "09232024.pdf"),
    (
        2024,
        8,
        8,
        "Chief Judge Kathleen Kerrigan announced today that Kashi Way and Adam B. Landy were sworn in as Judges of the United States Tax Court.",
        "08082024bv2.pdf",
    ),
    (
        2024,
        8,
        8,
        "Chief Judge Kathleen Kerrigan announced today that the United States Tax Court has adopted final amendments to its Rules of Practice and Procedure.",
        "08082024v3.pdf",
    ),
    (2024, 5, 30, "Tax Court Disciplinary Matters", "05302024.pdf"),
    (2024, 4, 25, "Charles Jeane becomes Clerk of the Court.", "04252024.pdf"),
    (2024, 3, 14, "In Memory of Judge John O. Colvin.", "03142024.pdf"),
    (2024, 2, 20, "Tax Court Disciplinary Matters.", "02202024.pdf"),
    (
        2024,
        2,
        16,
        "The Court announced today that Chief Judge Kathleen Kerrigan has been re-elected and will serve another two-year term beginning June 1, 2024.",
        "02162024.pdf",
    ),
    (
        2024,
        1,
        22,
        "Chief Judge Kathleen Kerrigan announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
        "01222024.pdf",
    ),
    (2023, 11, 28, "Tax Court Disciplinary Matters.", "11282023.pdf"),
    (
        2023,
        8,
        28,
        "Chief Judge Kathleen Kerrigan announced that Jennifer E. Siegel and Zachary S. Fried have been selected to serve as Special Trial Judges of the United States Tax Court.",
        "08282023.pdf",
    ),
    (2023, 8, 4, "Tax Court Disciplinary Matters.", "08042023.pdf"),
    (
        2023,
        5,
        8,
        "The U.S. Tax Court announced that the written examination for applicants other than attorneys at law (nonattorney applicants) for admission to practice before the U.S. Tax Court will be held remotely at 12:30pm EST on Wednesday, November 8, 2023, using the ExamSoft platform.",
        "05082023.pdf",
    ),
    (2023, 3, 20, "Tax Court Disciplinary Matters.", "03202023.pdf"),
    (
        2023,
        3,
        20,
        "Chief Judge Kathleen Kerrigan announced today that the United States Tax Court has adopted final amendments to its Rules of Practice and Procedure.",
        "08042023.pdf",
    ),
    (2022, 12, 16, "Tax Court Disciplinary Matters.", "12162022.pdf"),
    (2022, 11, 21, "Tax Court Disciplinary Matters.", "11212022.pdf"),
    (2022, 10, 26, "Tax Court Disciplinary Matters.", "10262022.pdf"),
    (2022, 10, 14, "In Memory of Judge Herbert Chabot.", "10142022.pdf"),
    (2022, 8, 25, "Tax Court Disciplinary Matters.", "08252022.pdf"),
    (
        2022,
        8,
        23,
        "The U.S. Tax Court has issued Administrative Order 2022-01, which repeals Administrative Orders 2021-02 and 2021-03, effective August 29, 2022.",
        "08232022.pdf",
    ),
    (2022, 6, 24, "Tax Court Disciplinary Matters.", "06242022.pdf"),
    (
        2022,
        6,
        3,
        "Beginning June 6, 2022, the Tax Court’s Washington, D.C. courthouse will be open to the public.",
        "06032022.pdf",
    ),
    (
        2022,
        4,
        1,
        "Chief Judge Maurice B. Foley announced today that, effective March 31, 2022, Special Trial Judge Daniel A. Guy, Jr. has retired.",
        "04012022.pdf",
    ),
    (
        2022,
        3,
        23,
        "Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
        "03232022.pdf",
    ),
    (2022, 3, 8, "In Memory of Judge Joel Gerber", "03082022.pdf"),
    (
        2022,
        2,
        25,
        "The United States Tax Court announced today that Judge Kathleen Kerrigan has been elected Chief Judge to serve a two-year term beginning June 1, 2022.",
        "02252022.pdf",
    ),
    (2022, 2, 18, "In Memory of Judge Robert P. Ruwe", "02182022.pdf"),
    (
        2022,
        2,
        2,
        "Since December 28, 2020, over 750 new features have been added to DAWSON, the Tax Court’s case-management system.",
        "02012022.pdf",
    ),
    (
        2022,
        1,
        26,
        "After assessing public health and other factors relating to nationwide COVID-19 cases, the U.S. Tax Court has determined that it is not appropriate to conduct in-person proceedings through February 25, 2022.",
        "01262022.pdf",
    ),
    (2022, 1, 24, "Tax Court Disciplinary Matters.", "01242022.pdf"),
    (
        2022,
        1,
        12,
        "After assessing public health and other factors relating to the rapid nationwide increase of COVID-19 cases, the U.S. Tax Court has determined that it is not appropriate to conduct in-person proceedings in January 2022.",
        "01122022.pdf",
    ),
    (
        2021,
        12,
        28,
        "Chief Judge Maurice B. Foley announced today that opinion search is now available in the DAWSON case management system.",
        "12282021.pdf",
    ),
    (
        2021,
        12,
        14,
        "Chief Judge Maurice B. Foley announced today that order search is now available in the DAWSON case management system.",
        "12142021.pdf",
    ),
    (
        2021,
        12,
        9,
        "From January 1, 2021, through November 30, 2021, the Court received 33,300 petitions.",
        "12092021.pdf",
    ),
    (
        2021,
        12,
        6,
        "On December 6, 2021, Chief Judge Maurice B. Foley announced that Adam B. Landy and Eunkyong Choi have each been selected to serve as a Special Trial Judge and taken the oath of office.",
        "12062021.pdf",
    ),
    (
        2021,
        11,
        19,
        "On November 18, 2021, Special Trial Judge Daniel A. Guy, Jr. received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.",
        "11192021.pdf",
    ),
    (2021, 10, 14, "Tax Court Disciplinary Matters.", "10142021.pdf"),
    (
        2021,
        10,
        5,
        "To provide guidance with respect to in-person proceedings, the Court has posted a new publication, Court Standards and Protocols to Protect Public Health, as well as issued Administrative Order 2021-02, Washington, D.C. Courthouse Access.",
        "10052021.pdf",
    ),
    (
        2021,
        8,
        27,
        "On August 27, 2021, the Court issued Administrative Order 2021-01, Policies for Remote (Virtual) Proceedings, which outlines the policies adopted allowing for both in-person and remote (virtual) trials.",
        "08272021.pdf",
    ),
    (
        2021,
        8,
        16,
        "The Court met with various stakeholders to address concerns relating to the increased number of petitions being filed and to limit the potential for premature assessment and enforcement action.",
        "08162021.pdf",
    ),
    (
        2021,
        7,
        23,
        "The United States Tax Court has received a significantly higher number of petitions this year. The Court is processing petitions expeditiously, but the increased volume has caused a delay between when a petition is received by the Court and when it is served on the Internal Revenue Service.",
        "07232021.pdf",
    ),
    (2021, 5, 21, "Tax Court Disciplinary Matters.", "05212021.pdf"),
    (
        2021,
        5,
        17,
        "The United States Tax Court announced today that the examination for admission to practice before the Court will be held remotely on Wednesday, November 17, 2021.",
        "05172021.pdf",
    ),
    (
        2021,
        4,
        5,
        "Chief Judge Maurice B. Foley announced today that the United States Tax Court will begin accepting applications for its new Diversity in Government Internship Program (DiG Tax).",
        "04052021.pdf",
    ),
    (2021, 2, 23, "Tax Court Disciplinary Matters.", "02232021.pdf"),
    (
        2021,
        2,
        12,
        "The Tax Court announces its Diversity & Inclusion Series. The series is comprised of webinars that will spotlight different trailblazers and their paths to, and success in, the field of tax law.",
        "02122021.pdf",
    ),
    (
        2021,
        1,
        11,
        "Chief Judge Maurice B. Foley announced today that DAWSON has been updated to include “Today’s Orders”.",
        "01112021.pdf",
    ),
    (
        2020,
        12,
        18,
        "Chief Judge Maurice B. Foley announced today that on December 28, 2020, the United States Tax Court will officially launch DAWSON (Docket Access Within a Secure Online Network), its new case management system.",
        "12182020.pdf",
    ),
    (
        2020,
        12,
        10,
        "Chief Judge Maurice B. Foley announced today that the Court has updated its guidance on procedures related to subpoenas for remote proceedings.",
        "12102020.pdf",
    ),
    (
        2020,
        11,
        30,
        "Senior Judge Robert P. Ruwe has fully retired and is no longer recalled for judicial service.",
        "11302020.pdf",
    ),
    (
        2020,
        11,
        20,
        "For paper documents requiring multiple signatures and postmarked November 21, 2020 through December 28, 2020, the Court has modified its signature requirements as outlined in Administrative Order 2020-05.",
        "11202020.pdf",
    ),
    (2020, 11, 16, "Tax Court Disciplinary Matters.", "11162020.pdf"),
    (
        2020,
        11,
        12,
        "Beginning Monday, November 16, 2020, the Court will resume accepting hand-delivered documents to the main courthouse building.",
        "11122020.pdf",
    ),
    (
        2020,
        10,
        29,
        "Effective Friday, October 30, 2020, and until further notice, the United States Tax Court will be suspending its in-person acceptance of hand-delivered documents.",
        "10292020.pdf",
    ),
    (
        2020,
        10,
        7,
        "To facilitate the transition to the Court's new case management system, beginning at 5:00 PM Eastern Time on November 20, 2020, the current e-filing system will become inaccessible and all electronic files will become read-only.",
        "10072020.pdf",
    ),
    (
        2020,
        9,
        9,
        "Chief Special Trial Judge Lewis R. Carluzzo received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.",
        "09092020.pdf",
    ),
    (2020, 8, 17, "Tax Court Disciplinary Matters.", "08172020.pdf"),
    (
        2020,
        8,
        6,
        "Chief Judge Maurice B. Foley announced additional guidance with respect to remote proceedings.",
        "08062020.pdf",
    ),
    (2020, 7, 20, "Tax Court Disciplinary Matters.", "07202020.pdf"),
    (
        2020,
        7,
        17,
        "Chief Judge Maurice B. Foley announced that, effective July 16, 2020, Senior Judge Joel Gerber has retired and is no longer recalled for judicial service.",
        "07172020.pdf",
    ),
    (
        2020,
        6,
        24,
        "Beginning July 10, 2020, the Clerk’s Office will accept hand-delivered documents between the hours of 8:00 AM and 4:30 PM, Monday through Friday.",
        "06242020.pdf",
    ),
    (2020, 6, 22, "Tax Court Disciplinary Matters.", "06222020.pdf"),
    (2020, 6, 19, "Mail delivery will resume on July 10, 2020.", "06192020.pdf"),
    (
        2020,
        5,
        29,
        "To accommodate continuing uncertainties relating to the COVID-19 pandemic, and until further notice, Court proceedings will be conducted remotely.",
        "05292020_proceedings.pdf",
    ),
    (
        2020,
        5,
        29,
        "The Court will resume accepting requests for photocopies of Court records from non- parties (copy requests) on June 1, 2020.",
        "05292020_copywork.pdf",
    ),
    (
        2020,
        5,
        18,
        "Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
        "05182020.pdf",
    ),
    (
        2020,
        5,
        7,
        "To mitigate risks and concerns related to COVID-19, the Court is postponing the November 2020 nonattorney examination to the fall of 2021.",
        "05072020.pdf",
    ),
    (
        2020,
        5,
        4,
        "The Court announced that attorney applications for admission to practice before the Court may be emailed to the Admissions Office.",
        "05042020.pdf",
    ),
    (
        2020,
        4,
        21,
        "Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
        "04212020_1.pdf",
    ),
    (2020, 4, 21, "Tax Court Disciplinary Matters.", "04212020_2.pdf"),
    (
        2020,
        3,
        23,
        "The United States Tax Court building remains closed and trial sessions through June 30, 2020 are canceled.",
        "03232020.pdf",
    ),
    (
        2020,
        3,
        18,
        "The Court announced that effective as of 9:00 PM on March 18, 2020, and until further notice, the United States Tax Court building is closed.",
        "03182020.pdf",
    ),
    (
        2020,
        3,
        13,
        "The Court has determined that it is appropriate to cancel certain trial sessions and to close the Court to visitors, effective immediately.",
        "03132020.pdf",
    ),
    (
        2020,
        3,
        11,
        "The Court has determined that it is appropriate to cancel certain trial sessions.",
        "03112020.pdf",
    ),
    (
        2020,
        2,
        24,
        "The Court announced that Chief Judge Maurice B. Foley has been re-elected and will serve another two-year term beginning June 1, 2020.",
        "02242020.pdf",
    ),
    (2020, 2, 21, "Tax Court Disciplinary Matters.", "02212020.pdf"),
    (
        2020,
        1,
        15,
        "The Tax Court has adopted amendments to its Rules of Practice and Procedure.",
        "01152020.pdf",
    ),
    (
        2019,
        11,
        25,
        "Chief Judge Maurice B. Foley announced that the United States Tax Court has proposed amendments to its Rules of Practice and Procedure.",
        "112519.pdf",
    ),
    (2019, 11, 22, "Tax Court Disciplinary Matters.", "112219.pdf"),
    (2019, 9, 23, "In Memory of Judge Arthur L. Nims III.", "092319.pdf"),
    (
        2019,
        9,
        4,
        "Chief Judge Maurice B. Foley announced the retirement of Special Trial Judge Robert N. Armen, Jr.",
        "090419.pdf",
    ),
    (
        2019,
        7,
        15,
        "The Tax Court has adopted amendments to its Rules of Practice and Procedure.",
        "071519.pdf",
    ),
    (2019, 7, 12, "Tax Court Disciplinary Matters.", "071219.pdf"),
    (
        2019,
        6,
        11,
        "On June 11, 2019, Chief Judge Maurice B. Foley announced that, effective as of June 7, 2019, Senior Judge Julian I. Jacobs has fully retired and is no longer recalled for judicial service.",
        "061119.pdf",
    ),
    (2019, 5, 17, "Tax Court Disciplinary Matters.", "051719.pdf"),
    (
        2019,
        5,
        10,
        "The Court issued Administrative Order No. 2019-01, outlining procedures for filing limited entries of appearance in Tax Court cases.",
        "051019.pdf",
    ),
    (2019, 4, 26, "Tax Court Disciplinary Matters.", "051019.pdf"),
    (2019, 3, 15, "Tax Court Disciplinary Matters.", "031519.pdf"),
    (
        2019,
        2,
        4,
        "The Tax Court has extended the period for submission of comments regarding interim and proposed partnership rules.",
        "020419.pdf",
    ),
    (
        2019,
        1,
        26,
        "Chief Judge Maurice B. Foley announced the resumption of full operations of the United States Tax Court effective Monday, January 28, 2019.",
        "012619.pdf",
    ),
    (
        2018,
        12,
        19,
        "The Tax Court has announced interim and proposed amendments to its Rules of Practice and Procedure.",
        "121918.pdf",
    ),
    (
        2018,
        11,
        30,
        "The Tax Court has adopted amendments to its Rules of Practice and Procedure.",
        "113018.pdf",
    ),
    (
        2018,
        11,
        30,
        "Tax Court Disciplinary Matters.",
        "113018_disciplinary_matters.pdf",
    ),
    (2018, 10, 12, "Tax Court Disciplinary Matters.", "101218.pdf"),
    (2018, 9, 25, "Tax Court Disciplinary Matters.", "092518.pdf"),
    (
        2018,
        9,
        24,
        "Chief Judge Maurice B. Foley announced the retirement of Judge Carolyn P. Chiechi.",
        "092418.pdf",
    ),
    (2018, 9, 6, "Tax Court Disciplinary Matters.", "090618.pdf"),
    (2018, 7, 20, "Tax Court Disciplinary Matters.", "072018.pdf"),
    (
        2018,
        5,
        8,
        "The Tax Court has issued a press release announcing the date and time of the 2018 written exam for admission to practice for applicants other than attorneys at law.",
        "050818.pdf",
    ),
    (2018, 4, 19, "Tax Court Disciplinary Matters.", "041918.pdf"),
    (
        2018,
        2,
        26,
        "Judge Maurice B. Foley will become Chief Judge June 1, 2018.",
        "022618.pdf",
    ),
    (
        2018,
        1,
        3,
        "Chief Judge L. Paige Marvel announced the retirement of Judge Robert A. Wherry, Jr.",
        "010318.pdf",
    ),
    (2017, 12, 21, "Tax Court Disciplinary Matters.", "122117.pdf"),
    (2017, 12, 21, "Tax Court Disciplinary Matters.", "122117.pdf"),
    (2017, 10, 13, "Tax Court Disciplinary Matters.", "101317.pdf"),
    (
        2017,
        9,
        15,
        "The 2018 Tax Court Judicial Conference will be held in Chicago, Illinois, on the campus of Northwestern University’s Pritzker School of Law in March.",
        "091517.pdf",
    ),
    (2017, 8, 31, "Tax Court Disciplinary Matters.", "083117.pdf"),
    (
        2017,
        5,
        12,
        "The Tax Court announced that Chief Special Trial Judge Peter J. Panuthos has decided to step down as Chief Special Trial Judge, effective September 1, 2017, and that Special Trial Judge Lewis R. Carluzzo has been named Chief Special Trial Judge, effective September 1, 2017.",
        "051217.pdf",
    ),
    (2017, 4, 13, "Tax Court Disciplinary Matters.", "041317.pdf"),
    (2017, 2, 17, "Tax Court Disciplinary Matters.", "021717.pdf"),
    (2016, 12, 16, "Tax Court Disciplinary Matters.", "121616.pdf"),
    (2016, 10, 12, "Tax Court Disciplinary Matters.", "101216.pdf"),
    (
        2016,
        7,
        18,
        "Chief Judge L. Paige Marvel has released a statement acknowledging the passing on July 15, 2016, of the Honorable Howard A. Dawson, Jr., the longest-serving judge in Tax Court history.",
        "071816.pdf",
    ),
    (
        2016,
        6,
        14,
        "The Chief Judge has announced the adoption of Rules for Judicial Conduct and Disability Proceedings for the United States Tax Court.",
        "061416.pdf",
    ),
    (2016, 5, 31, "Tax Court Disciplinary Matters.", "053116.pdf"),
    (
        2016,
        5,
        6,
        "The Tax Court has issued a press release announcing the date and time of the 2016 written exam for admission to practice for applicants other than attorneys at law.",
        "050616.pdf",
    ),
    (
        2016,
        3,
        28,
        "The Tax Court has announced interim and proposed amendments to its Rules of Practice and Procedure.",
        "032816.pdf",
    ),
    (
        2016,
        3,
        24,
        "Diana L. Leyden to be sworn in as a Special Trial Judge.",
        "032416.pdf",
    ),
    (
        2016,
        2,
        29,
        "Judge L. Paige Marvel will become Chief Judge June 1, 2016.",
        "022916.pdf",
    ),
    (2016, 2, 19, "Tax Court Disciplinary Matters.", "021916.pdf"),
    (
        2016,
        1,
        11,
        "The Tax Court has announced proposed amendments to its Rules of Practice and Procedure.",
        "011116.pdf",
    ),
    (2015, 12, 18, "Tax Court Disciplinary Matters.", "121815.pdf"),
    (2015, 10, 15, "Tax Court Disciplinary Matters.", "101515.pdf"),
    (2015, 8, 6, "Tax Court Disciplinary Matters.", "080615.pdf"),
    (2015, 7, 1, "Tax Court Disciplinary Matters.", "070115.pdf"),
    (2015, 5, 29, "Tax Court Disciplinary Matters.", "052915.pdf"),
    (2015, 4, 24, "Tax Court Disciplinary Matters.", "042415.pdf"),
    (2015, 2, 24, "Tax Court Disciplinary Matters.", "022415.pdf"),
    (2014, 12, 19, "Tax Court Disciplinary Matters.", "121914.pdf"),
    (2014, 11, 14, "Tax Court Disciplinary Matters.", "111414.pdf"),
    (
        2014,
        10,
        10,
        "The Court issued a press release in Amazon.Com, Inc. & Subsidiaries v. Commissioner of Internal Revenue.",
        "101014.pdf",
    ),
    (2014, 9, 5, "Tax Court Disciplinary Matters.", "090514.pdf"),
    (2014, 7, 18, "Tax Court Disciplinary Matters.", "071814.pdf"),
    (
        2014,
        5,
        13,
        "The Tax Court has issued a press release announcing the date and time of the 2014 written exam for admission to practice for applicants other than attorneys at law.",
        "051314.pdf",
    ),
    (2014, 4, 25, "Tax Court Disciplinary Matters.", "042514.pdf"),
    (2013, 12, 20, "Tax Court Disciplinary Matters.", "122013.pdf"),
    (2013, 9, 30, "Tax Court Disciplinary Matters.", "093013.pdf"),
    (2013, 6, 25, "Tax Court Disciplinary Matters.", "062513.pdf"),
    (2012, 9, 18, "In Memory of Judge Russell E. Train.", "091812.pdf"),
    (2012, 9, 11, "In Memory of Judge Lapsley W. Hamblen, Jr.", "091112.pdf"),
    (2012, 7, 13, "In Memory of Judge Renato Beghe.", "071312.pdf"),
    (
        2012,
        7,
        6,
        "The Tax Court has adopted amendments to its Rules of Practice and Procedure requiring electronic filing by most practitioners, providing privacy protections in whistleblower cases, and making other miscellaneous and conforming changes.",
        "070612.pdf",
    ),
    (
        2012,
        6,
        26,
        "The Tax Court announces a uniform method of spot-citing Memorandum Opinions.",
        "062612.pdf",
    ),
    (
        2012,
        6,
        12,
        "The Tax Court announces the investiture of Judge Kathleen Kerrigan.",
        "061212.pdf",
    ),
    (
        2012,
        5,
        8,
        "The Tax Court has issued a press release announcing the date and time of the 2012 written exam for admission to practice for applicants other than attorneys at law.",
        "050812.pdf",
    ),
    (
        2012,
        5,
        7,
        "Judge Michael B. Thornton has been elected as Chief Judge of the United States Tax Court to serve a 2-year term beginning June 1, 2012.",
        "050712.pdf",
    ),
    (
        2012,
        4,
        30,
        "Judge Robert P. Ruwe received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.",
        "043012.pdf",
    ),
    (
        2012,
        4,
        17,
        "Daniel A. Guy, Jr., will take the oath of office to serve as a Special Trial Judge of the United States Tax Court on May 31, 2012.",
        "041712.pdf",
    ),
    (
        2012,
        3,
        26,
        "Chief Special Trial Judge Peter J. Panuthos received the J. Edgar Murdock Award for distinguished service to the United States Tax Court.",
        "032612.pdf",
    ),
    (
        2012,
        3,
        6,
        "Comments received on proposed amendments to the Tax Court Rules of Practice and Procedure requiring electronic filing by most parties represented by counsel, providing privacy protections in whistleblower cases, and making other miscellaneous and conforming changes.",
        "030612.pdf",
    ),
    (
        2011,
        12,
        28,
        "The Tax Court has announced proposed amendments to its Rules of Practice and Procedure reducing the number of copies required for papers filed with the Court, requiring electronic filing by most parties represented by counsel, providing privacy protections in whistleblower cases, and making other miscellaneous and conforming changes.",
        "122811.pdf",
    ),
    (
        2011,
        6,
        17,
        "The Tax Court has added to its Internet Web site an “Orders” tab containing two new features to assist the public in identifying and locating orders issued by the Court: Today’s Designated Orders and Orders Search.",
        "061711.pdf",
    ),
    (
        2011,
        5,
        5,
        "The Tax Court has adopted amendments to its Rules of Practice and Procedure affecting time periods for filing summary judgment motions, Rule 155 computations, and motions regarding elections to proceed under the small tax case procedure, as well as other amendments to Rules and forms.",
        "050511.pdf",
    ),
    (
        2011,
        3,
        18,
        "Comments received on proposed amendments to the Tax Court Rules of Practice and Procedure affecting time periods for filing summary judgment motions, Rule 155 computations, motions regarding elections to proceed under the small tax case procedure, and answers in lien and levy cases, as well as other proposed amendments to Rules and forms.",
        "031811.pdf",
    ),
    (
        2010,
        12,
        23,
        "Chief Judge John O. Colvin announced today that H.R. 5901, relating to appointment of employees of the United States Tax Court, was passed by the United States Senate on December 17 and by the United States House of Representatives on December 22.",
        "122310.pdf",
    ),
    (
        2010,
        12,
        20,
        "The Tax Court has announced proposed amendments to its Rules of Practice and Procedure affecting time periods for filing summary judgment motions, Rule 155 computations, motions regarding elections to proceed under the small tax case procedure, and answers in lien and levy cases. It also proposes other amendments to its Rules and forms.",
        "122010.pdf",
    ),
    (
        2010,
        5,
        5,
        "The Tax Court has issued a press release announcing the date and time of the 2010 written exam for admission to practice for applicants other than attorneys at law.",
        "05052010_exam.pdf",
    ),
    (
        2009,
        11,
        20,
        "The Tax Court has adopted an amendment to its Rules of Practice and Procedure authorizing the electronic filing of documents in all Tax Court cases effective January 1, 2010. The Court is also considering a proposal requiring in the near future electronic filing for most parties represented by practitioners admitted to practice before the Court, and has invited comments on the proposed eFiling requirement to be received by the Court by December 21, 2009.",
        "112009.pdf",
    ),
    (
        2009,
        9,
        18,
        "The Tax Court has adopted amendments to various Rules of Practice and Procedure to conform them more closely with the Federal Rules of Civil Procedure.",
        "091809.pdf",
    ),
    (
        2009,
        3,
        27,
        "The Court has proposed amendments to conform its Rules of Practice and Procedure more closely with selected procedures from the Federal Rules of Civil Procedure.",
        "032709.pdf",
    ),
    (2008, 10, 9, "Judge Richard T. Morrison sworn in.", "100908_Morrison.pdf"),
    (2008, 10, 9, "Judge Richard T. Morrison sworn in.", "100908_Morrison.pdf"),
    (
        2008,
        10,
        3,
        "The Court has adopted amendments to its Rules of Practice and Procedure regarding whistleblower award actions and electronic service, and other amendments to its Rules and forms.",
        "100908_Morrison.pdf",
    ),
    (2008, 8, 4, "Judge David Gustafson sworn in.", "080408_Gustafson.pdf"),
    (2008, 8, 1, "Judge Elizabeth Crewson Paris sworn in.", "080408_Gustafson.pdf"),
    (
        2008,
        6,
        2,
        "The Court has proposed amendments to its Rules of Practice and Procedure regarding whistleblower award actions and electronic service, and other amendments to its Rules and forms.",
        "060208.pdf",
    ),
    (
        2008,
        4,
        30,
        "The Tax Court has issued a press release announcing the date and time of the 2008 written exam for admission to practice for applicants other than attorneys at law.",
        "043008.pdf",
    ),
    (
        2008,
        1,
        15,
        "The Court has adopted amendments to its Rules regarding privacy issues and access to its electronic case files, and other amendments to its Rules and forms.",
        "011508.pdf",
    ),
    (
        2007,
        12,
        27,
        "The Tax Court has announced that it has published on its web site requirements for Tax Clinics and Student Practice Programs.",
        "011508.pdf",
    ),
    (2007, 11, 27, "Announcement regarding Final Status Report.", "112707.pdf"),
    (2007, 8, 30, "In Memory of Special Trial Judge Carleton D. Powell.", "083007.pdf"),
    (2007, 8, 30, "Announcement regarding Final Status Report.", "083007.pdf"),
    (2007, 4, 26, "Announcement regarding Final Status Report.", "042607.pdf"),
    (
        2007,
        4,
        26,
        "The Court has adopted the privately funded seminars disclosure policy established by the Judicial Conference of the United States.",
        "042607.pdf",
    ),
    (
        2007,
        4,
        3,
        "Amendment to Rule 25(b), Tax Court Rules of Practice and Procedure, adopted.",
        "040307.pdf",
    ),
    (
        2007,
        2,
        16,
        "The Court has proposed amending its Rules of Practice and Procedure to include District of Columbia Emancipation Day, April 16, as a legal holiday for purposes of computing time.",
        "021607_release.pdf",
    ),
    (
        2007,
        1,
        16,
        "The Court has proposed amending its Rules of Practice and Procedure to address privacy issues and public access to its electronic case files and to make miscellaneous and conforming changes.",
        "011607.pdf",
    ),
    (
        2007,
        1,
        12,
        "Amendment to Rule 173(b), Tax Court Rules of Practice and Procedure, adopted.",
        "011207.pdf",
    ),
    (
        2006,
        11,
        28,
        "Comments regarding the proposed amendment to Rule 173(b), Tax Court Rules of Practice and Procedure, received, and effective date of the proposed amendment extended until further notice by the Court.",
        "112806.pdf",
    ),
    (
        2006,
        9,
        12,
        "The Court has proposed amending its Rules of Practice and Procedure, requiring the filing of answers by the Commissioner of Internal Revenue in all small tax cases.",
        "091206.pdf",
    ),
    (2006, 5, 3, "Written Exam for Admission to Practice Announced.", "050306.pdf"),
    (2006, 2, 28, "Judge John O. Colvin Elected Chief Judge.", "022806.pdf"),
    (
        2006,
        1,
        27,
        "The installation of a new telephone system necessitates changes to the Court's telephone numbers.",
        "012706.pdf",
    ),
    (
        2005,
        12,
        12,
        "The Court has proposed amending its Rules of Practice and Procedure by issuing an Interim Rule and Interim Procedures regarding the establishment of an electronic filing pilot program.",
        "121205_electronic_filing.pdf",
    ),
    (
        2005,
        12,
        6,
        "The Tax Court will begin accepting credit card payments presented in person at the courthouse and converting checks into electronic funds transfers on December 19, 2005",
        "120605.pdf",
    ),
    (
        2005,
        10,
        20,
        "The Court session scheduled to commence on October 24, 2005 in Miami, Florida, has been cancelled until further notice",
        "102005.pdf",
    ),
    (
        2005,
        9,
        21,
        "Amendments to Rules of Practice and Procedure Adopted",
        "092105.pdf",
    ),
    (
        2005,
        9,
        1,
        "The Court session scheduled for the week of November 14, 2005 in New Orleans, Louisiana, has been cancelled until further notice",
        "090105.pdf",
    ),
    (
        2005,
        7,
        7,
        "Proposed Amendments to the Rules of Practice and Procedure announced",
        "070705.pdf",
    ),
    (2005, 6, 20, "Robert R. Di Trolio Becomes Clerk of the Court", "062005.pdf"),
    (
        2004,
        11,
        2,
        "Retirement Announcement - Charles S. Casazza, Clerk of the Court",
        "110204.pdf",
    ),
    (
        2004,
        6,
        23,
        "Death Announcement - Senior Judge Charles E. Clapp, II",
        "062304.pdf",
    ),
    (
        2004,
        5,
        17,
        "Availability of Electronic (North) Courtroom announced and guidelines issued",
        "051704_Electronic_Courtroom.pdf",
    ),
    (
        2004,
        4,
        28,
        "Written Exam for Admission to Practice Announced",
        "051704_Electronic_Courtroom.pdf",
    ),
    (2004, 2, 23, "Judge Joel Gerber Elected Chief Judge", "022304.pdf"),
    (2003, 6, 30, "Judge Mark V. Holmes Sworn In", "063003_Holmes.pdf"),
    (
        2003,
        6,
        30,
        "Amendments to Rules of Practice and Procedure Adopted",
        "063003.pdf",
    ),
    (2003, 6, 17, "Judge Diane L. Kroupa Sworn In", "061703_Kroupa.pdf"),
    (2003, 4, 28, "Judge Robert A. Wherry, Jr. Sworn In", "042803_Wherry.pdf"),
    (2003, 4, 22, "Judge Joseph Robert Goeke Sworn In", "042203_Goeke.pdf"),
    (2003, 4, 22, "Judge Harry A. Haines Sworn In", "042203_Haines.pdf"),
    (2003, 2, 10, "Standing Pretrial Order Revised", "021003.pdf"),
    (
        2002,
        4,
        4,
        "Chief Judge Thomas B. Wells of the United States Tax Court announced that the written examination for admission to practice for applicants other than attorneys at law will be held 11/14/2002",
        "040402.pdf",
    ),
    (
        2002,
        2,
        25,
        "Chief Judge Thomas B Wells has been re-selected as Chief Judge of the United States Tax Court for a two year term",
        "022502.pdf",
    ),
    (
        2002,
        1,
        17,
        "Retired Judge Perry Shields of the United States Tax Court died on January 14, 2002, in Knoxville, Tennessee",
        "011702.pdf",
    ),
    (2001, 12, 3, "Resumption of Delivery of U.S. Mail", "120301.pdf"),
    (2001, 1, 5, "Death Announcement - Retired Judge Darrell D. Wiles", "010501.pdf"),
    (
        2001,
        1,
        3,
        "Death Announcement - Retired Judge William Miller Drennen",
        "010301.pdf",
    ),
    (2000, 4, 27, "Written Exam for Admission to Practice Announced", "042700.pdf"),
    (2000, 4, 13, "Death Announcement - Senior Judge William M. Fay", "041300.pdf"),
    (2000, 3, 20, "Death announcement - Senior Judge Lawrence A. Wright", "032000.pdf"),
    (2000, 2, 28, "Judge Thomas B. Wells Elected Chief Judge", "022800.pdf"),
    (
        2000,
        2,
        28,
        "Death Announcement - Retired Judge Jules G. Körner III",
        "022800.pdf",
    ),
]

# Reused from the retired press_release_body -> NewsItem migration script so
# environments where that migration already ran are not re-seeded.
PRESS_RELEASE_SEED_COMMAND_NAME = (
    "Press release data migration to snippets - Press releases"
)


class PressReleasesPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "news-and-announcements"
        title = "News and Announcements"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        press_release_page = PressReleasePage(
            title=title,
            slug=slug,
            seo_title=title,
            search_description="News and Announcements",
            show_in_menus=True,
        )

        home_page.add_child(instance=press_release_page)
        press_release_page.save_revision().publish()
        logger.info(f"'{title}' page created and published.")

        self._seed_news_items_from_press_release_history()

    def _seed_news_items_from_press_release_history(self):
        """
        One-time seed of historical press releases as NewsItem snippets, so
        fresh/sandbox installs have realistic News and Announcements content.
        """
        if ExecuteScript.command_exists(PRESS_RELEASE_SEED_COMMAND_NAME):
            logger.info(
                f"Script '{PRESS_RELEASE_SEED_COMMAND_NAME}' already exists. Skipping."
            )
            return

        script_entry = ExecuteScript.create_script(PRESS_RELEASE_SEED_COMMAND_NAME)
        current_user = get_user_model().objects.filter(is_superuser=True).first()

        try:
            created_count = 0
            for (
                year,
                month,
                day,
                description,
                doc_filename,
            ) in PRESS_RELEASE_NEWS_ITEMS:
                document = self.load_document_from_documents_dir(
                    subdirectory=None,
                    filename=doc_filename,
                    title=doc_filename,
                )

                publish_datetime = timezone.make_aware(datetime(year, month, day))
                expiration_datetime = publish_datetime + timedelta(days=7)

                news_item = NewsItem.objects.create(
                    title=description[:500],
                    description=description,
                    document=document,
                    publish_date=publish_datetime,
                    homepage_display_expiration_date=expiration_datetime,
                    live=True,
                )

                # NewsItem.save() unconditionally overwrites created_by/updated_by
                # with the first user, so set them (and created_at, to match
                # publish_date for historical ordering via
                # NewsItem.Meta.ordering = ["-created_at"]) through update()
                # to bypass save().
                NewsItem.objects.filter(pk=news_item.pk).update(
                    created_at=publish_datetime,
                    created_by=current_user,
                    updated_by=current_user,
                )

                created_count += 1

            logger.info(
                f"Created {created_count} NewsItem snippets from press release history."
            )

            script_entry.execution_status = "SUCCESS"
            script_entry.execution_log = (
                f"Seeded {created_count} NewsItem snippets from press release history."
            )
            script_entry.save()
        except Exception as e:
            script_entry.execution_status = "FAILURE"
            script_entry.execution_log = f"Failed to seed press release NewsItems: {e}"
            script_entry.save()
            raise
