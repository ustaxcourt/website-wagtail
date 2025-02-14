from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationRibbon
from home.models import EnhancedStandardPage


class PetitionersStartPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "petitioners_start"
        title = "Guidance for Petitioners: Starting A Case"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            Page.objects.get(slug=slug).delete()
            # return

        self.logger.write(f"Creating the '{title}' page.")

        navigation_ribbon = NavigationRibbon.objects.filter(
            name="Guidance for Petitioners Ribbon"
        ).first()

        questions = [
            {
                "question": "How do I start a case in the Tax Court?",
                "answer": 'You must file a <strong><a href="resources/forms/Petition_Kit.pdf" target="_blank" title="Petition Kit">petition</a></strong> to begin a case in the Tax Court. You can file a paper petition by mail or in person, or you can file an electronic petition through the Court\'s <strong><a href="https://ustaxcourt.gov/dawson.html" title="DAWSON">DAWSON</a></strong> system. <br/><br/>A party who files a petition in response to an IRS notice of deficiency, notice of determination, or notice of certification is called the "petitioner". The Commissioner of Internal Revenue is referred to as the "respondent" in Tax Court cases.',
                "anchortag": "START1",
            },
            {
                "question": "Who can file a petition with the Tax Court?",
                "answer": 'Anyone can file a petition who has received:<br/><br/><ol class="arabic-numbers"><li>A notice of deficiency,</li><li>A notice of determination, or</li><li>A notice of certification.</li></ol><br/>You can also file a petition (in certain circumstances) if you filed a claim with the IRS for relief from joint and several liability (innocent spouse relief), six months have passed, and the IRS has not issued you a determination letter.',
                "anchortag": "START2",
            },
            {
                "question": "Is there anyone who can help me file a petition and/or help me in my case against the IRS?",
                "answer": "Yes. You may hire an attorney or other person admitted to practice before the Tax Court to represent you before the Tax Court.<br/><br/>You might qualify for help from an organization referred to as a tax clinic. There are a number of tax clinics throughout the United States participating in the Tax Court's Clinical Program. You may want to contact a clinic in your geographic area. The Internal Revenue Service (Taxpayer Advocate Service) has a list of tax clinics on its Web site. The clinics have income restrictions, and a representative of the clinic will let you know whether you qualify to be represented. The Tax Court will send you information about tax clinics when you file your petition and when a Notice of Trial is sent to you.<br/><br/>There is additional help from organizations we refer to as calendar call programs. Tax practitioners volunteer their time to assist unrepresented low income taxpayers through professional organizations. If there is a participating Calendar Call Program in the city where you have requested trial, the judge may identify the volunteer practitioners at the beginning of the trial session.<br/><br/>These tax clinics and Bar-related calendar call programs are not part of the Internal Revenue Service or the Tax Court. The Tax Court does not endorse or recommend any particular tax clinic or Bar-related calendar call program.<br/><br/>You may be represented in your Tax Court case by a private attorney, a clinic representative, or other person admitted to practice before the Court. The agreement of representation is between you and the representative and is independent of the Tax Court or the IRS. Your representative must be admitted to practice before the Tax Court. All representatives who practice before the Tax Court are subject to the American Bar Association's Model Rules of Professional Conduct.",
                "anchortag": "START3",
            },
            {
                "question": "How can I find a tax clinic?",
                "answer": 'There are <strong><a href="https://ustaxcourt.gov/clinics.html" target="_blank" title="Clinics &amp;  Pro Bono Programs">tax clinics throughout the United States participating in the Tax Court\'s Clinical Program</a></strong>. You may want to contact one of the <strong><a href="https://ustaxcourt.gov/resources/clinics/clinics.pdf" target="_blank" title="Low Income Taxpayer Clinics">clinics</a></strong> in your geographic area. The Taxpayer Advocate of the Internal Revenue Service has a more <strong><a href="https://ustaxcourt.gov/redirect_clinic.html" target="_blank" title="Redirect Clinic">extensive clinic list</a></strong> available on the IRS Web site (<strong><a href="https://ustaxcourt.gov/redirect_irs.html" target="_blank" title="Redirect IRS">www.irs.gov</a></strong>). The Tax Court will send you information about tax clinics when you file your petition. The Court will also send tax clinic information when the Notice of Trial is sent to you. These tax clinics are not part of the Internal Revenue Service or the Tax Court. The Tax Court does not endorse or recommend any particular tax clinic or organization.',
                "anchortag": "START4",
            },
            {
                "question": "If I want to represent myself or if I don't qualify for representation by a tax clinic, can I represent myself?",
                "answer": 'You may file a petition with the Tax Court even if you do not have a representative. You may also present your case to a Judge without being represented. This guide is provided to help you in that process. If you decide to file a petition and to proceed to trial without a representative, you must pay close attention to all the Tax Court orders and notices you receive and all the instructions provided. A petitioner who is not represented is still required to abide by the <strong><a href="https://ustaxcourt.gov/rules.html" title="Rules of Practice and Procedure">Tax Court Rules of Practice and Procedure</a></strong> (Rules). If you have difficulty reading, writing, or understanding written instructions, you should seek help.',
                "anchortag": "START5",
            },
            {
                "question": "What should I do if I don't speak and/or understand English very well?",
                "answer": 'All proceedings in the Tax Court are in English. The Tax Court does not have staff available to assist non-English speaking petitioners. The <strong><a href="https://ustaxcourt.gov/rules.html" title="Tax Court Rules">Tax Court Rules</a></strong> provide that it is the responsibility of the parties to make arrangements for and compensate interpreters.<br/><br/>Many Low Income Taxpayer Clinics (LITCs) offer services in languages other than English. You can review <strong><a href="https://ustaxcourt.gov/resources/clinics/clinics.pdf" target="_blank" title="LITC List">the Court\'s list</a></strong> or the <strong><a href="https://ustaxcourt.gov/redirect_clinic.html" target="_blank" title="Redirect Clinic">Taxpayer Advocate\'s (IRS) more extensive list</a></strong> and find a clinic convenient to you that may provide the language assistance you need.',
                "anchortag": "START6",
            },
            {
                "question": "Are there any circumstances where the Court will help pay for the cost of an interpreter at trial?",
                "answer": "Ordinarily, the parties are expected to arrange for and compensate any needed interpreters. There may, however, be extraordinary situations in which the Court will compensate an interpreter. You may file a motion requesting that the Court pay the expenses of an interpreter. In your motion you must satisfy the Court that (1) a language barrier exists (you speak primarily a language other than English or you have a hearing impairment); (2) you do not have the financial means to pay for an interpreter; and (3) the case presents a substantial question which is not frivolous. A Judge has discretion to grant or deny your motion to pay the expenses of an interpreter.",
                "anchortag": "START7",
            },
            {
                "question": "If I need an interpreter at trial what should I do?",
                "answer": "You should make arrangements as early as possible to have an interpreter available. If you are unable to afford an interpreter, you should file a motion to request that the Court pay the expenses of an interpreter as soon as possible and generally no later than 30 days before trial. In your motion you should explain to the Court that you satisfy the three conditions set forth above: (1) A language barrier exists (you speak primarily a language other than English or you have a hearing impairment); (2) you do not have the financial means to pay for an interpreter; and (3) the case presents a substantial question which is not frivolous.",
                "anchortag": "START8",
            },
            {
                "question": "I thought I came to an agreement with the IRS, but the IRS sent me a notice of deficiency or a notice of determination stating that I have a right to file a petition with the Tax Court. Should I file a petition even though I thought my case was settled?",
                "answer": "It is difficult to know the circumstances in which you believe your case was settled. Because the IRS issued a notice, the IRS may be proceeding as if there is no settlement. To protect yourself against an unagreed assessment of tax or collection action, you should file a petition within the period set forth in the notice. You may also wish to contact the IRS about the status of your case.",
                "anchortag": "START9",
            },
            {
                "question": "If I decide to file a petition, what is the next step?",
                "answer": 'You can fill out a petition on the Tax Court website and print it, print out the petition form and fill it out, or fill in the petition form contained in the informational packet available from the Court. You may also file a petition online. For more information about eFiling a petition, refer to the Tax Court website at <strong><a href="https://ustaxcourt.gov/dawson.html" title="DAWSON">https://ustaxcourt.gov/dawson.html</a></strong>.',
                "anchortag": "START10",
            },
            {
                "question": "How do I fill out my petition?",
                "answer": '\n<strong>To eFile a petition, refer to the instructions and user guides available on the Tax Court website at </strong><strong><a href="https://ustaxcourt.gov/dawson.html" title="DAWSON">https://ustaxcourt.gov/dawson.html</a></strong><strong>.</strong><br/> <br/><strong>To file a paper petition:</strong><br/><br/>1. First, fill in your full name on the line at the top left of the petition. If you are a married couple filing a joint petition or if you were married in the tax year the return was filed and wish to file a joint petition, fill in both names on this line.<br/><br/>2. Next, check the appropriate box on line 1 for the type of case you intend to file. Place an X in the box that represents the type of letter you received from the IRS. For example, if you received a Notice of Deficiency, check that box. If you have a collection case, that is, the IRS has filed a Federal tax lien against property you own or has proposed a levy on your wages, bank accounts, State tax refunds, etc., and issued you a notice of determination, check the box for Notice of Determination Concerning Collection Action. If you received a notice of determination concerning a request for relief from joint and several liability (innocent spouse relief), or if you filed a claim with the IRS for relief from joint and several liability, six months have passed, and the IRS has not issued a determination letter, check the box marked Notice of Determination Concerning Your Request for Relief From Joint and Several Liability. Lastly, if you received a Notice of Determination Concerning Worker Classification, check that box. If you received a Final Determination for Disallowance of Interest Abatement, or if you requested abatement of interest and the IRS failed to make a determination within 180 days, check the box marked Notice of Final Determination for [Full/Partial] Disallowance of Interest Abatement Claim (or Failure of IRS to Make Final Determination Within 180 Days After Claim for Abatement). If you received a Notice of Certification of Your Seriously Delinquent Federal Tax Debt to the Department of State, check that box. Lastly, if you received a Notice of Determination Under Section 7623 Concerning Whistleblower Action, check that box.<br/><br/>3. On line 2, put the mailing date of the notice you received. You should also enter the city and State of the IRS office that issued you the notice.<br/><br/>4. Put the tax year(s) for which the notice was issued on line 3.<br/><br/>5. On line 4, you should choose whether you want your case conducted as a regular or small tax case and check the appropriate box. If you do not check a box, the Court will file your case as a regular case.',
                "anchortag": "START11",
            },
            {
                "question": "How do I decide whether to elect regular or small tax case procedures?",
                "answer": 'The tax laws provide for small tax case procedures for resolving disputes between taxpayers and the IRS. To have your case tried as a small tax case procedure, you must qualify and choose to have small tax case procedures applied to your case and the Tax Court must agree with your choice. Generally, the Tax Court will agree with your request if you qualify. For more information, see the <strong><a href="https://ustaxcourt.gov/case_procedure.html" title="Case Procedure Information">Case Procedure Information</a></strong> page.',
                "anchortag": "START12",
            },
            {
                "question": "What should I say in my petition?",
                "answer": "Line 5 of the petition asks you to tell the Court why you disagree with the IRS determination in your case. The eFiling petition prompts will ask for the same information. You should list clearly and concisely the errors that you believe the IRS made in the notice of deficiency or the notice of determination that was sent to you. List each issue separately using letters or numbers for each item, and briefly state why you disagree with the IRS. Be sure to list each item in the notice of deficiency or notice of determination with which you disagree. For example:<br/><br/>A. I disagree with the IRS's disallowance of my claim for head of household status because I satisfied the requirements for claiming that status.<br/><br/>B. I disagree with the IRS's disallowance of my dependent exemptions for my children because each of them satisfies the tests for dependency.<br/><br/>C. I disagree with the IRS's disallowance of my claim for the earned income credit because I correctly calculated the credit on my return.<br/><br/>Or:<br/><br/>I disagree with the IRS's determination that a levy be imposed on my wages because:<br/><br/>(1) such a levy would constitute a financial hardship for me and my family; and<br/><br/>(2) because I have proposed an alternative method of paying my federal tax liability.<br/><br/>On line 6 of the petition you should briefly state the facts on which you rely to support your position. List each statement of facts in the same order as you listed the issues on line 5. Clearly stating why you believe the IRS is wrong and what facts you rely upon will help the Tax Court understand your position.<br/><br/>Lastly, sign your name, preferably in blue ink, on the line for signature of petitioner. If you are filing a joint petition, be sure to have your spouse sign the petition as well. It is important that each signature be an original signature (and not a copy). Fill in your address and phone number on the lines provided. If the petition is a joint petition, your spouse must provide his or her address and phone number.<br/><br/>If you are filing a joint petition—paper or electronic—be sure to have your spouse sign the petition. It is important that each signature on a paper petition be an original signature (and not a copy). For electronic petition signature requirements, refer to the <strong><a href=\"https://ustaxcourt.gov/dawson_faqs.html\" title=\"DAWSON FAQs\">DAWSON FAQs</a></strong>. Fill in your address and phone number on the lines provided. If the petition is a joint petition, provide your spouse's address and phone number.",
                "anchortag": "START13",
            },
            {
                "question": "When should I file my petition?",
                "answer": "The tax laws set forth the different time limits for filing petitions in different kinds of cases. The IRS notice usually provides the number of days that you will have to file a petition, counting from the date the IRS notice was mailed to you. That date is usually stamped on the notice of deficiency or the notice of determination. In addition, the IRS notice may state the last date for filing the petition. The tax laws are very strict on filing dates and often do not allow extra time for filing a petition. For example, in a deficiency case, the petition must be filed by the 90th day (or the 150th day if the notice is addressed to a person outside the United States) from the date of the mailing of the notice of deficiency. The Tax Court cannot extend the time for filing a petition in response to a notice of deficiency. In a collection action, the petition should be filed within 30 days of the mailing of the notice of determination.",
                "anchortag": "START14",
            },
            {
                "question": "How do I file my petition?",
                "answer": '\n<strong><a href="https://ustaxcourt.gov/resources/forms/Petition_Simplified_Form_2.pdf" target="_blank" title="Petition Form 2">Paper petitions</a></strong> must be filed with the Tax Court in Washington, D.C. You may hand deliver it to the Tax Court between 8 a.m. and 4:30 p.m. (Eastern time), or mail it to:<br/><br/>United States Tax Court<br/>400 Second Street, N.W.<br/>Washington, D.C. 20217-0002<br/><br/>If you are unable to use the form from this Web site, write a letter to the Tax Court stating that you want to file a petition and that you would like any necessary forms and documents sent to you. The letter should include the amount in dispute, your name, your address, your telephone number, the year(s) at issue in your case, and a list of the errors you believe the IRS made. Include a copy of the IRS notice (see privacy discussion below) that you wish to dispute and follow the mailing procedures described above.<br/><br/>You may also file a petition electronically. E-filed petitions will be submitted electronically through the DAWSON case management system. For more information, see "Filing a Petition" at <strong><a href="https://ustaxcourt.gov/dawson.html" title="DAWSON">https://ustaxcourt.gov/dawson.html</a></strong>.',
                "anchortag": "START15",
            },
            {
                "question": "How can I protect the privacy of my Social Security number?",
                "answer": 'You should submit <strong><a href="https://ustaxcourt.gov/resources/forms/Form_4_Statement_of_Taxpayer_Identification_Number.pdf" target="_blank" title="Statement of Taxpayer Identification Numbeer">Form 4, Statement of Taxpayer Identification Number,</a></strong> when you file your petition, and redact (delete) your Social Security number or Employer Identification number from any notice you attach to your petition and from any other document you file with the Court. The word redact means to remove or delete information. See <strong><a href="https://ustaxcourt.gov/resources/ropp/Rule-27.pdf" target="_blank" title="Rule 27">Tax Court Rule 27</a></strong>. <strong>Do not include your Social Security number on any document you send to the Court (except Form 4).</strong>\n',
                "anchortag": "START16",
            },
            {
                "question": "How can I protect the privacy of personal information such as my financial account numbers?",
                "answer": "You should not include on, and where necessary you should redact or delete from, any document filed with the Court personal information such as Social Security numbers or Employer Identification numbers, dates of birth, names of minor children, and financial account numbers. See Rule 27(a). If you do not do so, your personal information will be part of the public record of your case. When information is part of the public record, it means that anyone can come to the Court and look at the file and obtain information.",
                "anchortag": "START17",
            },
            {
                "question": "How do I delete or redact my Social Security number or other private numbers from documents?",
                "answer": 'The simplest way to delete or redact is to use a black marker and black out the numbers or information you want to be private. For example, if the notice you received from the IRS has your Social Security number (000-00-0000), you should black out the number when you attach the notice to the petition. Do not write these numbers on your petition, or on any other documents submitted to the Court. You should write your Social Security number on <strong><a href="https://ustaxcourt.gov/resources/forms/Form_4_Statement_of_Taxpayer_Identification_Number.pdf" target="_blank" title="Statement of Taxpayer Identification Number">Form 4, Statement of Taxpayer Identification Number</a></strong>, which will not be available to the public.',
                "anchortag": "START18",
            },
            {
                "question": "What if I forget to redact or delete personal information?",
                "answer": 'You may send the Court within 60 days of the original filing of a document on which you inadvertently disclosed personal information a complete, redacted copy of the previously filed document for substitution in the record; the redacted document should be clearly marked "redacted" (under the docket number). You should explain that you want to substitute the redacted document for the previously submitted (unredacted) document. See Rule 27(h).',
                "anchortag": "START19",
            },
            {
                "question": "May I file my petition electronically or by fax?",
                "answer": 'The Tax Court does permit eFiling of petitions.  Refer to the user guides and other information on the Court\'s website at <strong><a href="https://ustaxcourt.gov/dawson.html" title="DAWSON">https://ustaxcourt.gov/dawson.html</a></strong>. <br/><br/>The Court does not accept filings of any document by fax or email.',
                "anchortag": "START20",
            },
            {
                "question": "How do I ensure that the petition is filed on time?",
                "answer": 'The petition must be received by the Court or mailed to the Court within the time specified in the Internal Revenue Code.  The Court\'s electronic filing system logs documents received using Eastern time. The IRS normally lists the last day for filing a timely petition with the Court in a notice of deficiency. <br/><br/>Generally, your petition will be treated as timely filed if the Tax Court receives it in an envelope bearing a legible U.S. Postal Service (USPS) postmark that is within the time for timely filing. There are safer alternatives to using regular first-class mail to mail a petition to the Court. Using certified or registered mail and obtaining a postmarked receipt from the USPS provides strong evidence that the petition was sent to the Tax Court on the certified or registered date of mailing. Another alternative is to use a <strong>DESIGNATED</strong> private delivery service.  You should be aware that not all services offered by private delivery companies are <strong>DESIGNATED</strong> private delivery services. Please review <strong><a href="https://ustaxcourt.gov/redirect_design_delivery.html" target="_blank" title="Redirect Designation of Private Delivery">IRS guidelines</a></strong> for what constitutes a <strong>DESIGNATED</strong> private delivery service. Using a <strong>DESIGNATED</strong> private delivery service provides strong evidence that the petition was sent to the Tax Court on either the date that is shown on the shipping label generated by the private delivery company or the date that is recorded electronically by the private delivery company to its database. <br/><br/>Caution: A private meter mail stamp or a "postmark" from a private, online postage-printing service will not prove that the petition was timely mailed.',
                "anchortag": "START21",
            },
            {
                "question": "My petition is due today. Is it too late to file a petition with the Tax Court?",
                "answer": 'No. You can file electronically, place your petition in the mail today, or hand deliver the petition to the Tax Court in Washington, D.C., today. (If the last day for filing is a Saturday, Sunday, or <strong><a href="https://ustaxcourt.gov/holidays.html" title="Legal Holidays">holiday</a></strong> in the District of Columbia, then you have until the next business day.) Using certified or registered mail or a designated private delivery service is preferable because it provides strong evidence that the petition was sent to the Tax Court on the registered mailing date. You will need a postmarked USPS registered mail or certified mail receipt or a receipt from a designated private delivery service.',
                "anchortag": "START22",
            },
            {
                "question": "Can I get an extension of time to file a petition?",
                "answer": "No. By law, the Tax Court cannot extend the time for filing a petition.",
                "anchortag": "START23",
            },
            {
                "question": "Does it cost anything to file a petition?",
                "answer": 'Yes. The filing fee is $60. You may pay by check, money order, or using Pay.gov.  <strong><a href="https://ustaxcourt.gov/pay_filing_fee.html" title="How to Pay the Filing Fee">See https://ustaxcourt.gov/pay_filing_fee.html</a></strong> for more information. ',
                "anchortag": "START24",
            },
            {
                "question": "How do I pay by check or money order?",
                "answer": 'Checks and money orders should be made payable to "Clerk, United States Tax Court". Please review our check policy and additional information on our <a href="https://www.ustaxcourt.gov/fees_and_charges.html">fees and charges page</a>.',
                "anchortag": "START25",
            },
            {
                "question": "Are there any circumstances where I do not have to pay the $60 filing fee?",
                "answer": 'Yes. The Tax Court may waive the filing fee if a petitioner establishes to the satisfaction of the Tax Court an inability to pay. The <strong><a href="https://ustaxcourt.gov/resources/forms/Application_for_Waiver_of_Filing_Fee.pdf" target="_blank" title="Application for Waiver of Filing Fee">Application for Waiver of Filing Fee</a></strong> requires detailed information and must be signed under penalty of perjury. If the petition is a joint petition (filed by a married couple), then you may file one waiver form which should be signed by both petitioners. If the Tax Court denies your request to waive the filing fee and you do not pay the filing fee, your case may be dismissed.',
                "anchortag": "START26",
            },
            {
                "question": "Must I pay the amount of tax that the IRS says I owe while my case is pending in the Tax Court?",
                "answer": "No, you do not usually need to pay the amount in dispute while your case is pending before the Tax Court. If the Tax Court ultimately concludes, however, that you owe some amount of tax, or if you settle or agree to an amount of tax liability, the law provides generally that interest runs on any unpaid tax from the date it was originally due until paid in full. Interest also runs on some penalties. Although you do not need to pay the amount in dispute while your case is pending in the Tax Court, you may do so if you want to stop the interest on the unpaid tax from accruing.<br/><br/>The rules regarding prepayment of tax and penalties differ in U.S. District Courts and the U.S. Court of Federal Claims. This guide does not provide information about the rules or procedures of those courts.",
                "anchortag": "START27",
            },
            {
                "question": "Should I include anything else with my petition?",
                "answer": "Yes. Attach to the petition a complete copy of the notice of deficiency, the notice of determination, or the notice of certification, including the explanation of adjustments or IRS Appeals Officer's report that you may have received with the notice of deficiency, the notice of determination, or the notice of certification. You should remove your Social Security number from the notice of deficiency or notice of determination. See Notice Regarding Privacy and Public Access to Case Files. Do not attach any other documents such as tax returns, copies of receipts, or other types of evidence to the petition.",
                "anchortag": "START28",
            },
            {
                "question": "Should I send anything else to the Tax Court when I file my petition?",
                "answer": 'Yes. You should also submit a <strong><a href="https://ustaxcourt.gov/resources/forms/Form_4_Statement_of_Taxpayer_Identification_Number.pdf" target="_blank" title="Statement of Taxpayer Identification Number">Statement of Taxpayer Identification Number </a></strong>(Form 4) and a <strong><a href="https://ustaxcourt.gov/resources/forms/Form_5_Request_for_Place_of_Trial.pdf" target="_blank" title="Request for Place of Trial">Request for Place of Trial</a></strong> (Form 5), which tells the Tax Court where you would like to have your trial held. Select from the list of <strong><a href="https://ustaxcourt.gov/dpt_cities.html" title="Places of Trial">cities</a></strong> in which the Tax Court holds trial sessions. <a href="https://www.ustaxcourt.gov/resources/images/city_map.gif" title="places of trail map">A map displaying the cities in which the Tax Court holds trial sessions</a> is also available.',
                "anchortag": "START29",
            },
            {
                "question": "Where may I request a place of trial if I elected to conduct my case as a small tax case?",
                "answer": 'If you elected to conduct your case as a small tax case, you may request a place of trial in any of the cities listed on <strong><a href="https://ustaxcourt.gov/resources/forms/Form_5_Request_for_Place_of_Trial.pdf" target="_blank" title="Request for Place of Trial">Form 5, Request for Place of Trial</a></strong>. Place an "X" in only one box to request your place of trial.',
                "anchortag": "START30",
            },
            {
                "question": "Where may I request a place of trial if I elected to conduct my case as a regular tax case?",
                "answer": 'If you elected to conduct your case as a regular case, you may request any of the cities not marked with an asterisk on <strong><a href="https://ustaxcourt.gov/resources/forms/Form_5_Request_for_Place_of_Trial.pdf" target="_blank" title="Request for Place of Trial">Form 5, Request for Place of Trial</a></strong>. Place an "X" in only one box to request your place of trial. You may not select one of the cities marked with an asterisk (*). If you are eFiling a petition, you will only be asked to choose from among the cities that are available for regular tax cases.',
                "anchortag": "START31",
            },
            {
                "question": "May I request trial in a more conveniently located city outside my state?",
                "answer": "Yes. You may select the city that is most convenient to you without regard to the state in which you live. However, if you elected to conduct your case as a regular tax case, you may not select one of the cities marked with an asterisk (*).",
                "anchortag": "START32",
            },
            {
                "question": "May I request that my case be heard remotely?",
                "answer": 'Yes. File a <strong><a href="https://ustaxcourt.gov/resources/forms/Motion_to_Proceed_Remotely.pdf" target="_blank" title="Motion to Proceed Remotely">Motion To Proceed Remotely</a></strong>. A Motion To Proceed Remotely may be filed at the time a petition is filed and up until 31 days before the first day of the trial session. The granting of the motion is at the Judge\'s discretion. If the Judge grants the Motion To Proceed Remotely, the parties will be provided with detailed instructions, including the date, time, and Zoomgov information for the remote (virtual) proceeding',
                "anchortag": "START33",
            },
            {
                "question": "How can I be sure that I have done everything correctly?",
                "answer": 'A checklist for Filing a paper <strong><a href="https://ustaxcourt.gov/resources/forms/Petition_Kit.pdf" target="_blank" title="Petition Kit">Petition</a></strong> is below. If you are eFiling a petition, see instead <strong><a href="https://ustaxcourt.gov/efile_a_petition.html" title="How to eFile a Petition">How to eFile a Petition</a></strong>.<br/><br/>Have I:<br/><br/><ul class="disc"><li>Printed my full name on the petition, signed the petition, and included my mailing address and telephone number?</li><li>If it is a joint petition, printed the name of my spouse and included my spouse\'s signature?</li><li>Included a check or money order for $60 made out to "Clerk, United States Tax Court"?</li><li>Filled in all information required on the petition form?</li><li>Completed the Statement of Taxpayer Identification Number (Form 4)?</li><li>Omitted or removed from the petition, from any enclosed notice of deficiency or notice of determination, and from any other document (other than Form 4) my Social Security number and certain other confidential personal and financial information as specified in the <strong><a href="https://ustaxcourt.gov/resources/forms/Privacy-_Notice.pdf" target="_blank" title="Privacy Notice">Notice Regarding Privacy and Public Access to Case Files</a></strong>?</li><li>Completed Form 5 (Request for Place of Trial) to indicate where I want to have my trial held?</li><li>Placed in an envelope the (1) original signed petition, (2) Statement of Taxpayer Identification Number, (3) Request for Place of Trial, and (4) check or money order for $60 for mailing to: United States Tax Court, 400 Second Street, N.W., Washington, D.C. 20217?</li><li>Either hand delivered the petition or mailed the petition using the U.S. Postal Service or a designated private delivery service and kept some evidence of the date I mailed the petition to the Tax Court (U.S. Postal Service postmarked certified or registered mail receipt or receipt from the designated private delivery service)?</li><li>Retained a copy of the petition for my records?</li></ul>The Court will send you a Notice of Receipt of Petition once your petition is received.',
                "anchortag": "START34",
            },
            {
                "question": "What can I do if I forgot to say everything I wanted to in my petition?",
                "answer": "You may want to file an amended petition. If so, you may be required by the Tax Court Rules to file a motion asking for leave to do so. If you are permitted to file an amended petition, you should indicate the additional facts and arguments in the amended petition.",
                "anchortag": "START35",
            },
            {
                "question": "After I file my petition, how many copies of any documents should I send the Tax Court if I decide I want to file anything else?",
                "answer": "You should mail a signed original and one copy of any document to the Tax Court. You also should send to the attorney representing the IRS a copy of any document you mail to the Tax Court. Do not forget to include your name and docket number at the top of any document you want to file with the Tax Court. <strong>However, do not include your Social Security Number on any document (other than Form 4) you file with the Tax Court</strong>. Do include your docket number on any documents you mail to the Court.",
                "anchortag": "START36",
            },
            {
                "question": "What happens after I file my petition?",
                "answer": 'If you filed a paper petition, you will receive a <strong><a href="https://ustaxcourt.gov/resources/taxpayer/Notice_of_Receipt_of_Petition.pdf" target="_blank" title="Notice of Receipt of Petition">notice of receipt of petition</a></strong> from the Tax Court by mail acknowledging the filing of the petition. That document will tell you the docket number of your case. If you eFiled your petition, the DAWSON system will provide the docket number. For example, if you file the petition in 2007, the last two digits will be -07. The docket number might look like 1234-07. If you chose, and the Tax Court granted, S case status, the docket number will contain the letter S at the end, for example, 1234-07S. You should include the docket number assigned to you on all letters and documents you send to the Tax Court and to the IRS. Next, an Answer is filed by the IRS. After your petition has been filed, you should send a copy of everything you send to the Tax Court to the attorney representing the IRS. The name and address of the IRS attorney is on the last page of the Answer.',
                "anchortag": "START37",
            },
            {
                "question": "How can I check on the status of my case?",
                "answer": 'Docket records are available through the Tax Court\'s website. The Court\'s case management system <strong><a href="https://dawson.ustaxcourt.gov/" target="_blank" title="DAWSON">DAWSON</a></strong> provides easy access to docket records by allowing you to search using a docket number or individual party name. Orders issued or entered and decisions entered after March 1, 2008, and Tax Court and memorandum opinions starting September 25, 1995 (summary opinions starting January 1, 2001), are available to the public through the Tax Court\'s website without registration for electronic access.<br/><br/>Complete instructions for using DAWSON are available under Reference Materials on the Tax Court\'s website at <strong><a href="https://ustaxcourt.gov/dawson.html" title="DAWSON">https://ustaxcourt.gov/dawson.html</a></strong>.',
                "anchortag": "START38",
            },
            {
                "question": "Who can I contact if I have questions?",
                "answer": 'Contact the Office of the Clerk for all case-related questions. You can contact the Tax Court by mail at U.S. Tax Court, 400 Second Street, N.W., Washington, D.C. 20217-0002 or by telephone at (202) 521-0700. <br/><br/>If you need assistance with DAWSON, the Tax Court\'s case management system, email <strong><a href="mailto:dawson.support@ustaxcourt.gov" title="Contact Support">dawson.support@ustaxcourt.gov</a></strong>. <br/><br/>A <strong><a href="https://ustaxcourt.gov/directory.html" title="Directory">directory</a></strong> is available on the Court\'s website.',
                "anchortag": "START39",
            },
            {
                "question": "Someone told me that if I want to ask the Tax Court to take some action affecting the other party, I should file a motion. What is a motion?",
                "answer": 'A motion is a request filed by one of the parties asking the Tax Court to take some action or asking the Tax Court to direct the other party to do something.<br/><br/>When you send a motion to the Tax Court, you should also send a copy of it to IRS counsel (and the other parties, if any, in the case). Attach a Certificate of Service to the copy you send to the Court. A sample Certificate of Service is available as Form 9 in <strong>Appendix I</strong> of the Rules; there is also a fillable <strong><a href="https://ustaxcourt.gov/resources/forms/Certificate_of_Service_Form_-9.pdf" target="_blank" title="Certificate of Service">Certificate of Service</a></strong> form on the Forms page. If you are filing a response to a motion electronically, please see the <strong>Petitioners\' Guide to Electronic Case Access and Filing</strong> for more information.',
                "anchortag": "START40",
            },
            {
                "question": "What are some of the common motions that can be filed?",
                "answer": '\n<ul class="disc"><li>Motion for continuance</li><li>Motion for leave to file an amended petition</li><li>Motion to change place of trial</li><li>Motion for summary judgment</li><li>Motion for submission of case fully stipulated (<strong><a href="https://ustaxcourt.gov/resources/ropp/Rule-122.pdf" target="_blank" title="Rule 122">Rule 122</a></strong>)</li><li>Motion for reconsideration of opinion</li><li>Motion to vacate decision</li></ul>',
                "anchortag": "START41",
            },
            {
                "question": "What is a motion for summary judgment? How should I respond to one?",
                "answer": '\n<strong>The motion.</strong> A motion for summary judgment requests a ruling from a judge on some or all of the issues in a case before trial. If a motion for summary judgment is filed, the judge will review the documents submitted by the parties and consider whether the case can be decided without a trial. The party filing the motion must show that there is no genuine dispute of any important fact and that the party filing the motion is entitled to judgment in their favor as a matter of law. See <strong><a href="https://ustaxcourt.gov/resources/ropp/Rule-121.pdf" target="_blank" title="Rule 121">Rule 121</a></strong>.<br/><br/><strong>Your response.</strong> If the Court orders you to file a response to a motion for summary judgment, your response must: specify which factual statements in the motion for summary judgment you dispute, state what you contend the actual facts are, and cite the specific evidence that you rely on to support your factual contentions. That is, you must do more than deny or disagree with the motion. Instead, you must set forth specific facts that establish there is a factual dispute and that a trial is necessary to resolve that dispute. It is not enough merely to claim that a fact is in dispute. You must support your claim that there is a question about a material fact (or facts) by submitting with your response the evidence on which you rely.<br/><br/><strong>Your evidence.</strong> Your supporting evidence may include your own sworn affidavit or unsworn declaration given under penalty of perjury. (<strong><a href="https://ustaxcourt.gov/resources/forms/Unsworn_Declaration_Form_18.pdf" target="_blank" title="Unsworn Declaration under Penalty of Perjury">Form 18, Unsworn Declaration under Penalty of Perjury</a></strong>). Your declaration can state facts about which you have personal knowledge. If your evidence includes documents, then you should submit those with your response (preferably numbered as Exhibits), and your declaration should identify and authenticate those documents. Your supporting evidence may also include other affidavits, stipulations, admissions, answers to interrogatories, or deposition transcripts.<br/><br/><strong>Legal disputes.</strong> A motion for summary judgment may involve not only factual disputes but also legal disputes. If you disagree with the IRS\'s explanation of the law that applies to your case, you should explain your disagreement and cite the statutes, regulations, or other authorities that apply to your case.<br/><br/><strong>Failure to respond.</strong> If the IRS files a motion for summary judgment in your case and the Court orders you to file a response, then your failure to file a response may be grounds for granting the motion. See <strong><a href="https://ustaxcourt.gov/resources/ropp/Rule-121.pdf" target="_blank" title="Rule 121">Rules 121(d)</a></strong> and <strong><a href="https://ustaxcourt.gov/resources/ropp/Rule-123.pdf" target="_blank" title="Rule 123">123(b)</a></strong>.<br/><br/><strong>Results of summary judgment.</strong> If a motion for summary judgment is granted in favor of the IRS, then there will be no trial, and a judgment will be entered against you. Similarly, if you file a motion for summary judgment and it is granted, then there will be no trial, and a judgment will be entered in your favor.',
                "anchortag": "START42",
            },
            {
                "question": "I would like to file a motion but I'm not sure what to title it. Will the Court correct the title of a motion (or other document) that is titled incorrectly?",
                "answer": "You are expected to submit a motion and other documents that are proper in title, form, and content. The Court expects filings to comply with the Court's Rules of Practice and Procedure. In some circumstances, the Court may retitle a motion or document to more clearly convey the contents and comply with the Tax Court Rules, or the Court may issue an order directing you to correct or supplement your document.",
                "anchortag": "START43",
            },
            {
                "question": "Where do I send responses to motions?",
                "answer": 'A response to a motion should be sent both to the Court and to respondent\'s counsel (and the other parties, if any, in the case). Attach a Certificate of Service to the copy you send to the Court. If you are filing a response to a motion electronically, see the <strong><a href="https://ustaxcourt.gov/dawson_user_guides.html" title="DAWSON User Guides">DAWSON User Guides</a></strong>.',
                "anchortag": "START44",
            },
            {
                "question": "I filed a timely petition with the Tax Court in a deficiency case. I received a letter from the IRS seeking to assess or collect the tax for the same tax year(s) I petitioned. What should I do?",
                "answer": "In a deficiency case, the IRS generally may not attempt to collect the amount in dispute while your case is pending in the Tax Court. You may consider filing a Motion To Restrain Assessment and Collection, and you should include a copy of the collection letter or notice you received from the IRS.",
                "anchortag": "START45",
            },
            {
                "question": 'What should I do if I receive a "no change" letter from the IRS after I file a petition in the Tax Court?',
                "answer": 'You should contact the IRS attorney, paralegal or Appeals officer handling your case and provide them with a copy of the "no change" letter. <strong>Be sure to redact your Social Security number from the "no change" letter</strong>. In most instances, the IRS will prepare a stipulated decision (an agreed decision) consistent with the "no change" letter. You and the IRS attorney should sign the stipulated decision and submit it to the Court. Your Tax Court case will be closed once the Judge enters the stipulated decision.',
                "anchortag": "START46",
            },
            {
                "question": "What happens if I can't find my copy of a document filed with the Tax Court?",
                "answer": 'The Tax Court is a court of public record and files are generally available for viewing in the Records Section at the Tax Court. You may also request that particular documents be copied by contacting the Reproduction Section by mail at United States Tax Court, 400 Second Street, N.W., Washington, D.C. 20217-0002 or by telephone at (202) 521-4683. There is a fee for copy work.<br/><br/>You may view, download, or print any document filed in your case if you have registered for electronic filing. You may also view any orders issued or entered and decisions entered after March 1, 2008, through <strong><a href="https://dawson.ustaxcourt.gov/" target="_blank" title="DAWSON">DAWSON</a></strong> on the Court\'s website without registering for electronic filing.',
                "anchortag": "START47",
            },
            {
                "question": "What if I move or change my address after I file a petition?",
                "answer": 'You should file a <strong><a href="https://ustaxcourt.gov/resources/forms/NOCOA_Form_10.pdf" target="_blank" title="Notice of Change of Address">Notice of Change of Address</a></strong> (Form 10) with the Tax Court. You should send a copy to the attorney representing the IRS. If you have moved to a new geographic area, you may want to change the place of trial to a city closer to your new address. If you want a different <strong><a href="https://ustaxcourt.gov/dpt_cities.html" title="Places of Trial">place of trial</a></strong>, you should send a Motion To Change Place of Trial to the Tax Court and send a copy to the IRS attorney. Please identify the city in which you now want your trial to be held.',
                "anchortag": "START48",
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Guidance for Petitioners - Starting a Case",
                body=[
                    {"type": "heading", "value": "Starting A Case"},
                    {"type": "questionanswers", "value": questions},
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
