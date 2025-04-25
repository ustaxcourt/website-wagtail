from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import ReleaseNotes

docs = {
    "Administrative_Order_2023-02.pdf": {
        "title": "Administrative Order 2023-02 - Expanding Remote Electronic Access to Certain Court Documents",
        "name": "Administrative_Order_2023-02.pdf",
    },
    "Rule-151_1_Amended_03202023.pdf": {
        "title": "Rule 151.1. Brief of an Amicus Curiae",
        "name": "Rule-151_1_Amended_03202023.pdf",
    },
    "Rule-27_Amended_03202023.pdf": {
        "title": "Rule 27. Privacy Protection for Filings Made With the Court",
        "name": "Rule-27_Amended_03202023.pdf",
    },
}


class DawsonReleaseNotesInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "release-notes"
        title = "DAWSON Release Notes"

        page = Page.objects.filter(slug=slug).first()
        if page:
            self.logger.write(f"- {title} page already exists. Updating...")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for doc in docs:
            docs[doc]["document"] = self.load_document_from_documents_dir(
                subdirectory=None,
                filename=docs[doc]["name"],
                title=docs[doc]["title"],
            )

        release_entries = [
            {
                "release_date": "2025-04-13",
                "description": """<ul>
                                    <li>New filters for Practitioner type, Practice type, Admissions Status, and Original Bar State are now present on the Practitioner Search page.</li>
                                    <li>Resolved issue that caused search terms in the Case, Order, Opinion, and Practitioner search fields to persist when it should be cleared.</li>
                                    <li>Resolved issue that caused a Docket Record filter to persist when is should be cleared.</li>
                                </ul>""",
            },
            {
                "release_date": "2025-04-05",
                "description": "<ul><li>Fixed a radio button formatting issue on the Petition workflow.</li></ul>",
            },
            {
                "release_date": "2025-03-30",
                "description": "<ul><li>Case procedure and Case type (i.e., docket suffix) filters have been added to the Case Search page.</li></ul>",
            },
            {
                "release_date": "2025-03-16",
                "description": "<ul><li>A logged in petitioner can no longer de-select their name as the filing party when eFiling a document.</li></ul>",
            },
            {
                "release_date": "2025-03-09",
                "description": "<ul><li>The following document types/event codes are no longer available in the dropdown picklist for Petitioners and Practitioners when eFiling a document:<ul><li>Application for Waiver of Filing Fee and Affidavit (APPW)</li><li>Civil Penalty Approval Form (CIVP)</li><li>Motion to Appoint New Tax Matters Partner (M044)</li><li>Motion to Calendar in the Electronic (North) Courtroom (M038)</li><li>Motion to Appoint an Interpreter Pursuant to Rule 143(f) (M045)</li><li>Motion to Certify for Interlocutory Appeal (M055)</li><li>Motion to Preclude (M085)</li><li>Motion to Shorten the Time (M102)</li><li>Notice of Clarification of Tax Matters Partner (NCTP)</li><li>Notice of Judicial Ruling (NRJR)</li><li>Notice of Relevant Judicial Decisions (NRJD)</li><li>Notice of Telephone Number (NTN)</li><li>Seriatim Answering Memorandum Brief (SAMB)</li><li>Seriatim Opening Memorandum Brief (SOMB)</li><li>Seriatim Reply Memorandum Brief (SRMB)</li><li>Seriatim Sur-Reply Memorandum Brief (SSRB)</li><li>Simultaneous Answering Memorandum Brief (SIMB)</li><li>Simultaneous Opening Memorandum Brief (SIOM)</li><li>Simultaneous Sur-Reply Memorandum Brief (SSRM)</li><li>Unsworn Declaration of [Name] under Penalty of Perjury in Support of [Document Name] (USDL)</li></ul></li><li>Motion to Appoint an Interpreter (M045A) is now available in the dropdown picklist for Petitioners and Practitioners when eFiling a document.</li></ul>",
            },
            {
                "release_date": "2025-02-23",
                "description": "<ul><li>Upgraded USWDS shared web services library to version 38.0.</li></ul>",
            },
            {
                "release_date": "2025-02-02",
                "description": "<ul><li>Motion to Supplement the Record (M129) is no longer available to use as a document type and has been replaced with a new document type: Motion to Complete or Supplement the Administrative Record (M129A). Prior filings of Motion to Supplement the Record (M129) are unaffected.</li><li>Resolved issue that caused users with a browser that was not updated to the latest version to experience an error when adding a PDF document to DAWSON.</li><li>Resolved styling accessibility issue on some public-facing pages.</li><li>Resolved an issue that caused an incorrect button/link to display for IRS or DOJ attorney's accessing DAWSON via a mobile device</li><li>Resolved the issue that caused a spinning wheel to display on the screen if a logged in user was idle for longer than 60 minutes and the system timed out. </li></ul>",
            },
            {
                "release_date": "2025-01-05",
                "description": "<ul><li>Document previews that previously displayed in a modal, now display in a new tab.</li><li>When viewing a case's docket record on a small screen, the docket number will now wrap to the next line if it can't be rendered on a single line due to the screen size.</li></ul><br/>",
            },
            {
                "release_date": "2024-12-15",
                "description": "<ul><li>Resolved the issue that caused practitioner contact information to not be updated appropriately in all cases when the Practitioner has a large number of cases and both physical address and email address were updated</li></ul><br/>",
            },
            {
                "release_date": "2024-12-08",
                "description": "<ul><li>All columns on the docket record are now sortable.</li><li>Data in the Action column on the docket record is now visible again to public non-logged in users or logged in users not associated with a case.</li><li>Resolved issue that caused users with a browser that was not updated to the latest version to experience an error when adding a PDF document to DAWSON. </li></ul><br/>",
            },
            {
                "release_date": "2024-12-04",
                "description": "<ul><li>Modification to Javascript used in search functionality.</li></ul>",
            },
            {
                "release_date": "2024-11-22",
                "description": '<ul><li>Updated the casing of words in all of the hover-over helper tips.</li><li>An updated view of scheduled trial sessions is now posted on the Court\'s website. Click on the <strong>About the Court</strong> menu and select <strong>Trial Sessions</strong>. Users may also navigate directly to the page by going here: <a title="Trial Sessions" href="https://dawson.ustaxcourt.gov/trial-sessions">https://dawson.ustaxcourt.gov/trial-sessions</a>.</li></ul>',
            },
            {
                "release_date": "2024-10-27",
                "description": '<ul><li>When there are no documents displayed on the docket record due to filtering, the messaging on the screen now displays "There are no documents of that type.".</li><li>The email verification link that is sent to users when they change their email address now expires after 24 hours. If the link does expire, users can now log in with their old email address and click a link to resend a new verification email.</li></ul>',
            },
            {
                "release_date": "2024-10-06",
                "description": "<ul><li>Resolved issue preventing upload of PDF files when the .pdf file extension contained one or more capital letters.</li></ul>",
            },
            {
                "release_date": "2024-09-29",
                "description": "<ul><li>Implemented messaging indicating possible root cause and link to troubleshooting steps to the user when they attempt to select a PDF that is too large, encrypted, password protected, or corrupted.</li></ul>",
            },
            {
                "release_date": "2024-09-15",
                "description": "<ul><li>E-filing Practitioners now have the option to 1) Answer some questions online and have DAWSON generate a petition document when creating a case, or 2) Upload a petition PDF document when creating a case. </li></ul>",
            },
            {
                "release_date": "2024-08-25",
                "description": '<ul><li>Resolved the issue that caused a spinning wheel to display on the screen if a logged in user was idle for longer than 60 minutes and the system timed out.</li><li>Draft, unserved, and stricken documents no longer display in the dropdown picklist when filing a document type that includes selecting a secondary document on the docket record.</li><li>The validation error message for the "What iteration is this filing?" field is now correctly aligned on the screen.</li><li>The petitioner phone number field that is available when filing a petition is now formatted appropriately for mobile device users.</li></ul>',
            },
            {
                "release_date": "2024-08-18",
                "description": '<ul><li>Removed the "Cancel Upload" link that would flash and then be hidden to the user on the modals displayed when uploading documents.</li><li>Removed an alert banner that provided incorrect information to logged in users when viewing cases where the petition was not yet served, and the user was not a party to.</li><li>When a user views any page in DAWSON via a supported browser, the USTC logo is now present on the right side of the browser tab.</li></ul>',
            },
            {
                "release_date": "2024-07-31",
                "description": "<ul><li>E-filing Petitioners now have the option to 1) Answer some questions online and have DAWSON generate a petition document when creating a case, or 2) Upload a petition PDF document when creating a case.</li></ul>",
            },
            {
                "release_date": "2024-07-28",
                "description": "<ul><li>DOJ employees that have a DAWSON account can now only enter appearances in cases that are in the case status On Appeal.</li></ul>",
            },
            {
                "release_date": "2024-07-21",
                "description": "<ul><li>E-filed petitions and attachments to the petition can now be viewed on the docket record by the e-filer prior to the petition being served to the IRS.</li></ul>",
            },
            {
                "release_date": "2024-06-30",
                "description": "<ul><li>The log in button on the sign in page is no longer displaying as inactive if a user saves their log in credentials in their browser settings.</li></ul>",
            },
            {
                "release_date": "2024-06-23",
                "description": '<ul><li>Implemented practitioner search for public users:<ul><li>Includes practitioner name search</li><li>Includes practitioner Tax Court Bar number search</li></ul></li><li>The "Request Access To Case" button that displays for practitioners has been relabeled "Represent a Party".</li><li>The document type picklist of available options in the "File First IRS Document" workflow is now revised to display more appropriate document types for first IRS filings to a case.</li><li>Resolved issue that caused document preview links on the review pages to not open the documents on iOS devices.</li><li>Added a new pop-up message that informs the user that DAWSON was updated if the user was logged in during a release.</li></ul>',
            },
            {
                "release_date": "2024-06-09",
                "description": "<ul><li>The PDF icon no longer displays on the review screen when a party uploads a document(s) to a case.</li></ul>",
            },
            {
                "release_date": "2024-06-02",
                "description": "<ul><li>Entry of Appearance is now available in the document picklist when an IRS Practitioner files the first document to a case.</li><li>Removed the duplicative confirmation checkmark that displayed when a user uploaded a document(s) to a case.</li><li>Added punctuation to the filing fee footnote that displays on the My Cases page and on the Case Information card. </li></ul>",
            },
            {
                "release_date": "2024-05-19",
                "description": "<ul><li>State dropdown lists are no longer abbreviated.</li><li>Resolved issue that caused some users to experience an error message when using the forgot password workflow.</li></ul>",
            },
            {
                "release_date": "2024-05-12",
                "description": "<ul><li>DAWSON users can now log in with any combination of upper-case or lower-case letters in their email address; Email addresses are no longer case-sensitive.</li><li>Resolved the issue that caused a TypeError on the Public API.</li></ul>",
            },
            {
                "release_date": "2024-04-28",
                "description": '<ul><li>The "Country" data field options for Petitioner/Practitioner contact information are now displayed as radio button selections rather than in a dropdown.</li><li>Motion to Lift Stay of Proceedings is now a document type that can be e-filed/added to the docket record.</li><li>Updated the confirmation banner text a user receives after filing documents in all cases in a consolidated group.</li><li>Resolved issue that caused some large documents that were uploaded to the docket record to have missing coversheets and display 0 pages in length.</li></ul>',
            },
            {
                "release_date": "2024-03-24",
                "description": "<ul><li>Eliminated the occurrence of an extra space to be unintentionally included with the password reset code when copying/pasting from an email message.</li></ul>",
            },
            {
                "release_date": "2024-03-17",
                "description": '<ul><li>New login page for DAWSON access implemented at <a href="https://dawson.ustaxcourt.gov/login" title="DAWSON login">https://dawson.ustaxcourt.gov/login</a>.</li></ul>',
            },
            {
                "release_date": "2024-03-10",
                "description": '<ul><li>Petitioners and Practitioners creating a new case in DAWSON no longer have to combine the IRS Notice (if they received one) and the Petition in a PDF file. Users can now upload an IRS Notice(s) separately from the Petition upload step. Once the case is submitted to the Court, the IRS Notice(s) that is uploaded is titled "Attachment to Petition" on the docket record.</li></ul>',
            },
            {
                "release_date": "2024-03-03",
                "description": '<ul><li>Resolved issue that caused some public users to experience a 502 error after clicking on the printable docket record link for cases that have a large number of documents on the docket record.</li><li>Implemented additional code to reduce the probability of a e-filer receiving the "Your Request Was Not Completed" warning modal when uploading documents. View the recorded webinar.</li></ul>',
            },
            {
                "release_date": "2024-01-21",
                "description": "<ul><li>The option for private practitioners to auto-generate an Entry of Appearance PDF is now available for any party, regardless of service preference.</li><li>Resolved issue that caused users that were associated with thousands of cases to receive a 504 error upon logging in.</li><li>Resolved issue that caused the auto-generated Entry of Appearance document title to get renamed during the filing process.</li></ul>",
            },
            {
                "release_date": "2024-01-07",
                "description": "<ul><li>Updated the Case Search page to display the Country filter as radio buttons and changed the default to search for both International and United States in the search results.</li><li>The option for practitioners to auto-generate an Entry of Appearance PDF is now only available if all parties to the case receive electronic service.  The option to upload a PDF is still available for all practitioners filing an Entry of Appearance regardless of the party's service preference.</li><li>The My Cases page no longer displays the docket number link for the lead case if a party only has access to a member case(s) in a consolidated group.</li></ul>",
            },
            {
                "release_date": "2023-12-10",
                "description": "<ul><li>Updated instructional text on the Petition e-filing flow.</li><li>Petitioners and Private Practitioners can now view the Filing Fee status for each case on the My Cases Dashboard view.</li><li>Resolved issue that caused an error when Practitioners not associated with any cases updated their contact information in DAWSON.</li></ul>",
            },
            {
                "release_date": "2023-12-03",
                "description": '<ul><li>Implemented a new look and feel for the DAWSON Account Creation page and added a "Create Account" link on the DAWSON homepage.</li></ul>',
            },
            {
                "release_date": "2023-10-22",
                "description": "<ul><li>Resolved issue that could result in practitioners incorrectly filing Entries of Appearance in multiple cases in a consolidated group.</li><li>Resolved issue that could result in a document upload error when practitioners filed an Entry of Appearance on a case.</li></ul>",
            },
            {
                "release_date": "2023-10-15",
                "description": "<ul><li>Enhanced the error messaging that is displayed if a user uploads an encrypted, corrupt, or non-PDF file. Closing this error message no longer returns the user to the beginning of the flow.</li><li>Fixed the case count on the My Cases page for users that are a party on multiple consolidated cases.</li></ul>",
            },
            {
                "release_date": "2023-10-01",
                "description": "<ul><li>Practitioners now have the option to either automatically generate an Entry of Appearance document or upload a PDF when filing an Entry of Appearance on a case.</li></ul>",
            },
            {
                "release_date": "2023-09-17",
                "description": "<ul><li>Resolved issue preventing some logged in users from viewing documents on the docket record on a mobile device.</li><li>Improved the Advanced Search menu display for logged in practitioners on a mobile device.</li><li>Improved the formatting for longer addresses on the Notice of Receipt of Petition to display appropriately in an envelope window.</li><li>Improved system performance when updating contact information across a large number of cases.</li></ul>",
            },
            {
                "release_date": "2023-08-27",
                "description": "<ul><li>Resolved display issues impacting Public Orders search for Standing Pretrial Orders and Standing Pretrial Orders for Small Cases.</li><li>Public users and parties to a case can now sort the docket record by date or by document number.</li><li>Improved the docket record display view for mobile devices.</li></ul>",
            },
            {
                "release_date": "2023-08-20",
                "description": "<ul><li>Practitioners that are associated with a large number of cases no longer receive a 504 error when logging in to DAWSON.</li></ul>",
            },
            {
                "release_date": "2023-08-13",
                "description": f'<ul><li>Updated feature allowing for public visibility of briefs for consolidated groups of cases consistent with <a href="{docs["Administrative_Order_2023-02.pdf"]["document"].file.url}" title="Administrative Order 2023-02">Administrative Order 2023-02</a>.</li></ul>',
            },
            {
                "release_date": "2023-08-01",
                "description": f'<ul><li>As identified in <a href="{docs["Administrative_Order_2023-02.pdf"]["document"].file.url}" title="Administrative Order 2023-02">Administrative Order 2023-02</a>, certain documents filed on or after August 1, 2023, in non-sealed cases will now be viewable by the public through DAWSON:<ul><li>Stipulated Decisions</li><li>Post-trial briefs e-filed by practitioners</li><li>Amicus briefs filed pursuant to <a href="{docs["Rule-151_1_Amended_03202023.pdf"]["document"].file.url}" title="Rule 151.1">Rule 151.1</a></li></ul></li><li>Beginning with the Fall 2023 term, an additional Notice of Trial will be served on pro se petitioners approximately a month before the scheduled trial date.</li></ul>',
            },
            {
                "release_date": "2023-07-16",
                "description": "<ul><li>Designation of Counsel to Receive Service has been removed as an option from all eFiling document menus.</li></ul>",
            },
            {
                "release_date": "2023-07-09",
                "description": '<ul><li>Replaced Year fields with Date Filed Start Date and Date Filed End Date fields on the Case Search Page.</li><li>Resolved issue where the "Coming Soon" text would briefly display next to the Order and Opinion header on the DAWSON Case Search page.</li></ul>',
            },
            {
                "release_date": "2023-07-05",
                "description": '<ul><li>Parties to consolidated cases now have the ability to electronically file documents simultaneously in all of the consolidated cases. Entries of Appearance for <strong>petitioner representatives</strong> and Decisions must still be filed in each case separately. Refer to the <a href="/dawson-user-guides" title="DAWSON User guides">DAWSON User Guides</a> for detailed instructions on how to electronically file documents in consolidated cases.</li><li>Parties to at least one case in a consolidated group of cases now have the ability to view documents on the docket record in all of the consolidated cases in the group.</li></ul>',
            },
            {
                "release_date": "2023-04-30",
                "description": "<ul><li>Resolved issue where help text was overlapping the text in the link to download the Corporate Disclosure Statement form.</li></ul>",
            },
            {
                "release_date": "2023-04-25",
                "description": f'<ul><li>Added a new checkbox for e-filers to acknowledge that their documents have been redacted in accordance with <a href="{docs["Rule-27_Amended_03202023.pdf"]["document"].file.url} title="Rule 27">Rule 27</a>.</li></ul>',
            },
            {
                "release_date": "2023-04-02",
                "description": '<ul><li>Parties no longer receive validation errors when e-filing a Motion for Leave or Motion for Leave to File Out of Time associated with an iteration type document.</li><li>"U.S.A." is no longer displayed as part of a Petitioner\'s address in the envelope window for paper service.</li></ul>',
            },
            {
                "release_date": "2023-03-26",
                "description": "<ul><li>Parties can now indicate that something is the nth version when e-filing certain documents (e.g., Fifteenth Amended Petition, etc.).</li></ul>",
            },
            {
                "release_date": "2023-03-19",
                "description": '<ul><li>Added "Motions" as an option to the Docket Record filter.</li><li>Updated DAWSON to reflect changes to the Tax Court Rules of Practice and Procedure effective March 20, 2023.</li><li>Improved login efficiency for users associated with a high number of cases.</li></ul>',
            },
            {
                "release_date": "2023-03-05",
                "description": "<ul><li>Consolidated case icons have been updated.</li></ul>",
            },
            {
                "release_date": "2023-01-08",
                "description": "<ul><li>Resolved issue preventing mobile DAWSON users from using the docket record's sorting and filtering features.</li></ul>",
            },
            {
                "release_date": "2022-12-04",
                "description": "<ul><li>The Sort By filter display on the docket record view now retains the correct filter selection when logged in users navigate to different views within a case.</li></ul>",
            },
            {
                "release_date": "2022-11-20",
                "description": "<ul><li>Logged-in Petitioners can now search for other cases by docket number from the My Cases screen without needing to log out.</li><li>Resolved issue that impacted printing the docket record in consolidated cases. </li></ul>",
            },
            {
                "release_date": "2022-11-01",
                "description": "<ul><li>Transcripts less than 90 days from the date of the proceeding no longer display a hyperlink.</li></ul>",
            },
            {
                "release_date": "2022-10-30",
                "description": "<ul><li>Parties to a case can now see the Consolidated Cases card on the Case Information Overview screen of their case(s) if any of their cases are part of a consolidated group.</li></ul>",
            },
            {
                "release_date": "2022-10-16",
                "description": "<ul><li>The docket record can now be filtered so that users can view only Orders on the docket record.</li></ul>",
            },
            {
                "release_date": "2022-09-18",
                "description": "<ul><li>The docket record can now be filtered so that parties to a case can view only those docket entries coded with exhibit-related event codes.</li><li>The Today's Orders page now sorts orders processed in consolidated cases appropriately.</li></ul>",
            },
            {
                "release_date": "2022-08-21",
                "description": "<ul><li>Corrected rules reference on the Notice of Receipt of Petition.</li></ul>",
            },
            {
                "release_date": "2022-08-14",
                "description": "<ul><li>Updated the text on the Opinion Search page to reflect all Online Cited Sources in opinions after July 1, 2016, can be viewed on the associated docket record.</li></ul>",
            },
            {
                "release_date": "2022-07-17",
                "description": "<ul><li>Resolved issue where Practitioners experience a blank white screen when searching for a sealed case by docket number.</li></ul>",
            },
            {
                "release_date": "2022-07-10",
                "description": "<ul><li>Any online sourced citations in opinions filed after July 11, 2022, can now be viewed directly from the associated docket record.</li></ul>",
            },
            {
                "release_date": "2022-06-12",
                "description": "<ul><li>Added additional help text regarding how to gain eAccess to existing cases and how to pay the filing fee to the initial screen that a petitioner sees when first registering for an account.</li></ul>",
            },
            {
                "release_date": "2022-06-05",
                "description": "<ul><li>Coversheets for Notice of Change of Email Address, Notice of Change of Telephone Number, and Notice of Change of Address now include the docket index entry number of the document. </li></ul>",
            },
            {
                "release_date": "2022-05-15",
                "description": '<ul><li>Cover sheets now include the docket index entry number of the document (e.g., the petition would have a "Document No. 1" on the coversheet).</li></ul>',
            },
            {
                "release_date": "2022-05-05",
                "description": '<ul><li>The "Filed By" value for private practitioner e-filed case access documents now reflect the name of the actual filer, not the party they represent.</li><li>If a pro se petitioner\'s requested place of trial has a low income taxpayer clinic available, a notice will now be automatically appended to the Notice of Receipt of Petition and the Notice Setting Case for Trial.</li></ul>',
            },
            {
                "release_date": "2022-03-27",
                "description": "<ul><li>Implemented style change to Orders generated in DAWSON to conform to the Court's new style guide requirements.</li></ul>",
            },
            {
                "release_date": "2022-03-06",
                "description": '<ul><li>Improved document upload process</li><li>Improved formatting of the title "Notice of Change of Email Address" on the docket record</li></ul>',
            },
            {
                "release_date": "2022-01-09",
                "description": "<ul><li>Improved consistency for headers across multiple page orders</li></ul>",
            },
            {
                "release_date": "2021-12-27",
                "description": '<ul><li>Implemented opinion search for public users.<ul><li>Includes keyword and phrase search.</li><li>Includes ability to find exact matches with "" (quotation marks) ex: "Premium Tax Credit".</li><li>Includes ability to combine two or more keywords or phrases with the (plus sign) ex: "fraud" "sanctions".</li><li>Includes ability to find documents with one or more keywords or phrases with the | (pipe character) ex: "fraud" | "sanctions" [Note: this search will return documents with the words fraud or sanctions].</li><li>Includes ability to filter by date, judge, case title, petitioner name, or docket number.</li><li>Includes ability to filter by opinion type.</li></ul></li></ul>',
            },
            {
                "release_date": "2021-12-19",
                "description": "<ul><li>Updated the Notice of Receipt of Petition form.</li><li>Added Motion to Proceed Remotely to the dropdown list of available documents.</li><li>Improved system time-out function to minimize disruptions during active use.</li></ul>",
            },
            {
                "release_date": "2021-12-13",
                "description": '<ul><li>Implemented Order search for public users<ul><li>Includes keyword and phrase search</li><li>Includes ability to find exact matches with "" (quotation marks) ex: "innocent spouse"</li><li>Includes ability to combine two or more keywords or phrases with the + (plus sign) ex: "collection due process" + remand</li><li>Includes ability to find documents with one or more keywords or phrases with the | (pipe character) ex: Lien | levy [Note: this search will return documents that contain the words "lien" or "levy"]</li><li>Includes ability to filter by date, judge, case title, petitioner name, or docket number</li></ul></li><li>Petitions and other documents with form fields now upload correctly for all browsers</li></ul>',
            },
            {
                "release_date": "2021-11-10",
                "description": "<ul><li>Petitioner service preference and email address update correctly after a petitioner gains eAccess to a previously-started case.</li></ul>",
            },
            {
                "release_date": "2021-10-19",
                "description": "<ul><li>A Notice of Change of Email Address will now be generated when a party's email is first added to DAWSON, or an existing address is changed.</li></ul>",
            },
            {
                "release_date": "2021-10-11",
                "description": "<ul><li>Parties can now e-file documents in cases closed longer than 6 months.</li></ul>",
            },
            {
                "release_date": "2021-09-19",
                "description": "<ul><li>Parties can no longer be served documents in a case if the petition is not yet served.</li><li>DAWSON can now be placed in Maintenance Mode if there is ever a need for system downtime.</li></ul>",
            },
            {
                "release_date": "2021-08-29",
                "description": "<ul><li>Removed Notice of Change of Address, Notice of Change of Phone Number, and Notice of Change of Address and Phone Number from documents that may be electronically filed [Note: User should update address and/or phone number within DAWSON]</li></ul>",
            },
            {
                "release_date": "2021-08-15",
                "description": "<ul><li>Improved deployment processes</li><li>Improved service process</li></ul>",
            },
            {
                "release_date": "2021-07-18",
                "description": "<ul><li>Improved error messaging and logging for application failures.</li><li>Improved phone number formatting.</li><li>Improved consistency of served party code display on docket record.</li></ul>",
            },
            {
                "release_date": "2021-07-11",
                "description": "<ul><li>Improved alignment of document links.</li><li>Removed the deployed timestamp on startup.</li><li>Improved link to view practitioner information within case.</li></ul>",
            },
            {
                "release_date": "2021-07-01",
                "description": "<ul><li>eAccess is now available to all petitioners, intervenors, and participants.</li><li>Improved format of printable docket record.</li></ul>",
            },
            {
                "release_date": "2021-06-23",
                "description": "<ul><li>Improved parties' display on the Review Your Filing screen.</li><li>Improved keyboard navigation.</li></ul>",
            },
            {
                "release_date": "2021-06-22",
                "description": "<ul><li>Improved validation on consolidated cases.</li></ul>",
            },
            {
                "release_date": "2021-06-19",
                "description": '<ul><li>Improvements made to the user interface:<ul><li>"Petitioner", "Respondent", and "Other" tabs under Case Information have been combined into a one "Party" tab.</li><li>Counsel is now listed on the same screen as the party they represent.</li><li>Intervenor/Participant subtab will only appear if there is an intervenor or participant on the case.</li><li>eAccess is now available for secondary petitioners.</li></ul></li><li>Improved consistency with respect to Entered &amp; Served date on all dispositive documents.</li></ul>',
            },
            {
                "release_date": "2021-06-10",
                "description": "<ul><li>Improved pagination for eFiled documents.</li></ul>",
            },
            {
                "release_date": "2021-06-06",
                "description": '<ul><li>Added "Not Served" indicator on Document Detail for unserved Petitions viewed on mobile devices.</li><li>Revised the Review Your Case screen for disclosure cases so that "Disclosure1" now reads "Disclosure".</li><li>Added scrolling for eFiling a document.</li><li>Revised Certificate of Service date format on printable Receipt of Filing.</li><li>Revised capitalization on Docket Number search for mobile devices.</li><li>Revised eFiling success message styling.</li><li>Improved validation messaging from shifting submit buttons on advanced case search.</li><li>Changed petitioner address font on Notice of Receipt of Petition.</li><li>Public Docket Record now populates served Parties column.</li></ul>',
            },
            {
                "release_date": "2021-05-01",
                "description": "<ul><li>Improvement: Increased maximum character count for the title of a lodged document submitted with a Motion for Leave.</li></ul>",
            },
            {
                "release_date": "2021-04-21",
                "description": "<ul><li>Practitioners can now update their firm name.</li></ul>",
            },
            {
                "release_date": "2021-04-18",
                "description": "<ul><li>Improved accessibility for screen-readers.</li><li>Implemented logic to ensure that Corrected and Revised Transcripts are viewable to the parties 90 days after the proceeding.</li></ul>",
            },
            {
                "release_date": "2021-04-11",
                "description": "<ul><li>Improvement: Receipt of Filing now displays the accurate Eastern Standard time the document was filed.</li></ul>",
            },
            {
                "release_date": "2021-03-28",
                "description": "<ul><li>Improvement: Today's Orders can be sorted by time served (oldest to newest and vice versa) and page count (highest to lowest and vice versa).</li></ul>",
            },
            {
                "release_date": "2021-03-20",
                "description": "<ul><li>Improvement:  Transcripts with trial/hearing dates more than 90 days ago are visible to parties.</li></ul>",
            },
            {
                "release_date": "2021-03-07",
                "description": '<ul><li>Improvement: The Court can provide petitioners with electronic access to their existing cases. Petitioners should submit a request to <strong><a data-original-title="Contact Support" href="mailto:dawson.support@ustaxcourt.gov" title="Email DAWSON support">dawson.support@ustaxcourt.gov</a></strong> and a letter with additional information will be mailed to them.</li><li>Improvement: The Printable Docket Record now includes counsel information for both parties.</li><li>Users can now preview PDF documents that are larger than 2MB before eFiling.</li></ul>',
            },
            {
                "release_date": "2021-02-22",
                "description": '<ul><li>Improvement: Petitioners and practitioners can change the email used for login and service through their DAWSON account.</li><li>Improvement: Bench Opinions now display as part of Today\'s Opinions.</li><li>The DAWSON application itself now provides a link to these release notes. See "What\'s New in DAWSON" in the footer next to the link for "Frequently Asked Questions".</li></ul>',
            },
            {
                "release_date": "2021-01-31",
                "description": "<ul><li>Electronic signatures visible in all PDF previews</li><li>Improvement to public docket record display of consistent event codes, filings, and proceedings<ul><li>All lodged documents show on the Docket Record with the event code ofMISCL.</li><li>Parenthetical text (i.e. Attachments, Certificate of Service, Objections) now display as part of the Filings and Proceedings for all views of the Docket Record.</li></ul></li></ul>",
            },
            {
                "release_date": "2021-01-25",
                "description": '<ul><li>Improvement: Text fields<ul><li>Document free text fields can now accept up to 1000 characters, and will show a helpful error message when the limit is reached.</li><li>The complete document title now accepts up to 3000 characters total, and will inform the user when the limit is reached.</li></ul></li><li>Left-align titles that expand to multiple lines on the "Today\'s Orders" table</li></ul>',
            },
            {
                "release_date": "2021-01-17",
                "description": "<ul><li>Improve consistent application of cover sheets</li><li>Improve accuracy of page counts shown on Docket Record</li></ul>",
            },
            {
                "release_date": "2021-01-10",
                "description": "<ul><li>Implement posting of Today's Orders</li><li>Improve mobile scrolling for Printable Docket Record</li><li>Allow petitioner names with special characters (') in case search</li><li>Improve mobile viewing of PDFs on the \"Review Your Case\" screen</li></ul>",
            },
        ]

        new_page = home_page.add_child(
            instance=ReleaseNotes(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=None,
                search_description=title,
                paragraph='See below for more information about additional code deployed to DAWSON since its launch on December 28, 2020. For questions or comments email <a href="mailto:dawson.support@ustaxcourt.gov" title="dawson.support@ustaxcourt.gov">dawson.support@ustaxcourt.gov</a>.',
                release_entries=[
                    (
                        "release_entry",
                        {
                            "release_date": entry["release_date"],
                            "description": entry["description"],
                        },
                    )
                    for entry in release_entries
                ],
            )
        )

        new_page.save_revision().publish()
