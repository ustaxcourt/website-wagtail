from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage
import logging

logger = logging.getLogger(__name__)


body = [
    {
        "type": "paragraph",
        "value": "On this page you will find the Court's current Rules of Practice and Procedure, forms, and fee schedule. You will also find information regarding past amendments to the Rules.",
    },
    {"type": "hr", "value": True},
    {"type": "h2", "value": "Rules of Practice and Procedure"},
    {
        "type": "links",
        "value": {
            "class": "with-bullets",
            "links": [
                {
                    "title": "Complete Rules of Practice and Procedure (current through amendments of August 8, 2024)",
                    "icon": None,
                    "document": "Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf",
                    "url": None,
                },
                {
                    "title": "Individual Rules by Title",
                    "icon": None,
                    "document": None,
                    "url": "#ROPP",
                },
                {
                    "title": "Forms",
                    "icon": None,
                    "document": None,
                    "url": "/case-related-forms",
                },
                {
                    "title": "Fee Schedule",
                    "icon": None,
                    "document": None,
                    "url": "/fees-and-charges",
                },
                {
                    "title": "Judicial Conduct and Disability Procedures",
                    "icon": None,
                    "document": None,
                    "url": "/jcdp",
                },
            ],
        },
    },
    {"type": "hr", "value": True},
    # Add Rules Amendments section
    {"type": "h2", "value": "Rules Amendments"},
    {
        "type": "links",
        "value": {
            "class": "with-bullets",
            "links": [
                {
                    "title": "Guide to Rules Amendments and Notes",
                    "icon": None,
                    "document": "Guide_to_Rules_Amendments_and_Notes.pdf",
                    "url": None,
                },
                {
                    "title": "Notices of Rule Amendments",
                    "icon": None,
                    "document": None,
                    "url": "/notices-of-rule-amendments",
                },
                {
                    "title": "Comments and Suggestions",
                    "icon": None,
                    "document": None,
                    "url": "/rules_comments",
                },
            ],
        },
    },
    {"type": "hr", "value": True},
    {
        "type": "heading",
        "value": {
            "text": "Rules of Practice and Procedure",
            "id": "ROPP",
            "level": "h2",
        },
    },
    {
        "type": "paragraph",
        "value": 'NOTE: In order to reduce download time, each Rule has been stored as a separate PDF file. The Rules may be purchased in loose-leaf form from the Clerk\'s Office for $20.00 by writing to the United States Tax Court, 400 Second Street, N.W., Washington, D.C. 20217, and enclosing a check or money order for that amount payable to the "Clerk, United States Tax Court." Please do not send cash.<br><br>Adobe Acrobat Reader is required to view and print the Rules of Practice and Procedure. Adobe Acrobat Reader can be obtained free of charge from <a href="https://acrobat.adobe.com/us/en/acrobat/pdf-reader.html" target="_blank">www.adobe.com</a>.',
    },
    {"type": "hr", "value": True},
    {
        "type": "h3",
        "value": "Title I. Rulemaking Authority, Scope of Rules, Publication, Construction, Effective Date, Definitions",
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 1. Rulemaking Authority, Scope of Rules, Publication of Rules and Amendments, Construction",
                    "icon": None,
                    "document": "Rule-1_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 2. Effective Date",
                    "icon": None,
                    "document": "Rule-2.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 3. Definitions",
                    "icon": None,
                    "document": "Rule-3_Amended_03202023.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title II. The Court"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 10. Name, Office, and Sessions",
                    "icon": None,
                    "document": "Rule-10_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 11. Payments to the Court",
                    "icon": None,
                    "document": "Rule-11(superseded).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 12. Court Records",
                    "icon": None,
                    "document": "Rule-12(superseded).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 13. Jurisdiction",
                    "icon": None,
                    "document": "Rule-13_amended_08082024.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {
        "type": "h3",
        "value": "Title III. Commencement of Case, Service and Filing of Papers, Form and Style of Papers, Appearance and Representation, Computation of Time",
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 20. Commencement of Case",
                    "icon": None,
                    "document": "Rule-20_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 21. Service of Papers",
                    "icon": None,
                    "document": "Rule-21_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 22.  Filing",
                    "icon": None,
                    "document": "Rule-22(amended).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 23. Form and Style of Papers",
                    "icon": None,
                    "document": "Rule-23_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 24. Appearance and Representation",
                    "icon": None,
                    "document": "Rule-24(amended-Oct.-6,-2020).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 25. Computation of Time",
                    "icon": None,
                    "document": "Rule-25_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 26. Electronic Filing",
                    "icon": None,
                    "document": "Rule-26_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 27. Privacy Protection for Filings Made With the Court",
                    "icon": None,
                    "document": "Rule-27_Amended_03202023.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title IV. Pleadings"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 30. Pleadings Allowed",
                    "icon": None,
                    "document": "Rule-30.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 31. General Rules of Pleading",
                    "icon": None,
                    "document": "Rule-31_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 32. Form of Pleadings",
                    "icon": None,
                    "document": "Rule-32_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 33. Signing of Pleadings",
                    "icon": None,
                    "document": "Rule-33_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 34. Petition",
                    "icon": None,
                    "document": "Rule-34_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 35. Entry on Docket",
                    "icon": None,
                    "document": "Rule-35_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 36. Answer",
                    "icon": None,
                    "document": "Rule-36_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 37. Reply",
                    "icon": None,
                    "document": "Rule-37.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 38. Joinder of Issue",
                    "icon": None,
                    "document": "Rule-38(amended).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 39. Pleading Special Matters",
                    "icon": None,
                    "document": "Rule-39.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 40. Defenses and Objections Made by Pleading or Motion",
                    "icon": None,
                    "document": "Rule-40.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 41. Amended and Supplemental Pleadings",
                    "icon": None,
                    "document": "Rule-41_amended_08082024.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title V. Motions"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 50. General Requirements",
                    "icon": None,
                    "document": "Rule-50.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 51. Motion for More Definite Statement",
                    "icon": None,
                    "document": "Rule-51.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 52. Motion To Strike",
                    "icon": None,
                    "document": "Rule-52.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 53. Motion To Dismiss",
                    "icon": None,
                    "document": "Rule-53.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 54. Timely Filing and Joinder of Motions",
                    "icon": None,
                    "document": "Rule-54.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 55. Motion To Restrain Assessment or Collection or To Order Refund of Amount Collected",
                    "icon": None,
                    "document": "Rule-55.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 56. Motion for Review of Jeopardy Assessment or Jeopardy Levy",
                    "icon": None,
                    "document": "Rule-56.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 57. Motion for Review of Proposed Sale of Seized Property",
                    "icon": None,
                    "document": "Rule-57..pdf",
                    "url": None,
                },
                {
                    "title": "Rule 58. Miscellaneous",
                    "icon": None,
                    "document": "Rule-58.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title VI. Parties"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 60. Proper Parties; Capacity",
                    "icon": None,
                    "document": "Rule-60(amended).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 61. [Reserved]",
                    "icon": None,
                    "document": "Rule-61_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 62. Misjoinder of Parties",
                    "icon": None,
                    "document": "Rule-62_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 63. Substitution of Parties; Change or Correction in Name",
                    "icon": None,
                    "document": "Rule-63_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 64. Intervention",
                    "icon": None,
                    "document": "Rule-64_Amended_03202023.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title VII. Discovery"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 70. General Provisions",
                    "icon": None,
                    "document": "Rule-70_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 71. Interrogatories",
                    "icon": None,
                    "document": "Rule-71.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 72. Production of Documents, Electronically Stored Information, and Things",
                    "icon": None,
                    "document": "Rule-72.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 73. Examination by Transferees",
                    "icon": None,
                    "document": "Rule-73.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 74. Depositions for Discovery Purposes",
                    "icon": None,
                    "document": "Rule-74_Amended_03202023.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title VIII. Depositions To Perpetuate Evidence"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 80. General Provisions",
                    "icon": None,
                    "document": "Rule-80.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 81. Depositions in Pending Case",
                    "icon": None,
                    "document": "Rule-81_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 82. Depositions Before Commencement of Case",
                    "icon": None,
                    "document": "Rule-82.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 83. Depositions After Commencement of Trial",
                    "icon": None,
                    "document": "Rule-83.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 84. Depositions Upon Written Questions",
                    "icon": None,
                    "document": "Rule-84.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 85. Objections, Errors, and Irregularities",
                    "icon": None,
                    "document": "Rule-85.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title IX. Admissions and Stipulations"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 90. Requests for Admission",
                    "icon": None,
                    "document": "Rule-90_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 91. Stipulations for Trial",
                    "icon": None,
                    "document": "Rule-91_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 92. [Reserved]",
                    "icon": None,
                    "document": "Rule-92_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 93. Identification and Certification of Administrative Record in Certain Actions",
                    "icon": None,
                    "document": "Rule-93_Amended_03202023.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {
        "type": "h3",
        "value": "Title X. General Provisions Governing Discovery, Depositions and Requests for Admission",
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 100. Applicability",
                    "icon": None,
                    "document": "Rule-100.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 101. Sequence, Timing, and Frequency",
                    "icon": None,
                    "document": "Rule-101.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 102. Supplementation of Responses",
                    "icon": None,
                    "document": "Rule-102.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 103. Protective Orders",
                    "icon": None,
                    "document": "Rule-103_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 104. Enforcement Action and Sanctions",
                    "icon": None,
                    "document": "Rule-104.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XI. Pretrial Conferences"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 110. Pretrial Conferences",
                    "icon": None,
                    "document": "Rule-110_Amended_03202023.pdf",
                    "url": None,
                }
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XII. Decision Without Trial"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 120. Judgment on the Pleadings",
                    "icon": None,
                    "document": "Rule-120.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 121. Summary Judgment",
                    "icon": None,
                    "document": "Rule-121_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 122. Submission Without Trial",
                    "icon": None,
                    "document": "Rule-122.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 123. Default and Dismissal",
                    "icon": None,
                    "document": "Rule-123.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 124. Alternative Dispute Resolution",
                    "icon": None,
                    "document": "Rule-124.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XIII. Calendars and Continuances"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 130. Motions and Other Matters",
                    "icon": None,
                    "document": "Rule-130.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 131. Trial Calendars",
                    "icon": None,
                    "document": "Rule-131.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 132. Special or Other Calendars",
                    "icon": None,
                    "document": "Rule-132.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 133. Continuances",
                    "icon": None,
                    "document": "Rule-133_Amended_03202023.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XIV. Trials"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 140. Place of Trial",
                    "icon": None,
                    "document": "Rule-140_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 141. Consolidation; Separate Trials",
                    "icon": None,
                    "document": "Rule-141_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 142. Burden of Proof",
                    "icon": None,
                    "document": "Rule-142.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 143. Evidence",
                    "icon": None,
                    "document": "Rule-143(amended).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 144. Exceptions Unnecessary",
                    "icon": None,
                    "document": "Rule-144.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 145. Exclusion of Proposed Witnesses",
                    "icon": None,
                    "document": "Rule-145.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 146. Determination of Foreign Law",
                    "icon": None,
                    "document": "Rule-146.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 147. Subpoenas",
                    "icon": None,
                    "document": "Rule-147_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 148. Fees and Mileage",
                    "icon": None,
                    "document": "Rule-148.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 149. Failure To Appear or To Adduce Evidence",
                    "icon": None,
                    "document": "Rule-149.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 150. Record of Proceedings",
                    "icon": None,
                    "document": "Rule-150.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 151. Briefs",
                    "icon": None,
                    "document": "Rule-151_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 151.1. Brief of an Amicus Curiae",
                    "icon": None,
                    "document": "Rule-151_1_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 152. Oral Findings of Fact or Opinion",
                    "icon": None,
                    "document": "Rule-152_Amended_03202023.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XV. Decision"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 155. Computation by Parties for Entry of Decision",
                    "icon": None,
                    "document": "Rule-155.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 156. Estate Tax Deduction Developing At or After Trial",
                    "icon": None,
                    "document": "Rule-156.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 157. Motion To Retain File in Estate Tax Case Involving Section 6166 Election",
                    "icon": None,
                    "document": "Rule-157.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XVI. Posttrial Proceedings"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 160. Harmless Error",
                    "icon": None,
                    "document": "Rule-160.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 161. Motion for Reconsideration of Findings or Opinion",
                    "icon": None,
                    "document": "Rule-161_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 162. Motion To Vacate or Revise Decision",
                    "icon": None,
                    "document": "Rule-162.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 163. No Joinder of Motions Under Rules 161 and 162",
                    "icon": None,
                    "document": "Rule-163.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XVII. Small Tax Cases"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 170. General",
                    "icon": None,
                    "document": "Rule-170_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 171. Election of Small Tax Case Procedure",
                    "icon": None,
                    "document": "Rule-171_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 172. Representation",
                    "icon": None,
                    "document": "Rule-172.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 173. Pleadings",
                    "icon": None,
                    "document": "Rule-173.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 174. Trial",
                    "icon": None,
                    "document": "Rule-174.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XVIII. Special Trial Judges"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 180. Assignment",
                    "icon": None,
                    "document": "Rule-180_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 181. Powers and Duties",
                    "icon": None,
                    "document": "Rule-181.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 182. Cases in Which the Special Trial Judge Is Authorized To Make the Decision",
                    "icon": None,
                    "document": "Rule-182_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 183. Other Cases",
                    "icon": None,
                    "document": "Rule-183.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XIX. Appeals"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 190. How Appeal Taken",
                    "icon": None,
                    "document": "Rule-190.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 191. Preparation of the Record on Appeal",
                    "icon": None,
                    "document": "Rule-191.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 192. Bond To Stay Assessment and Collection",
                    "icon": None,
                    "document": "Rule-192.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 193. Appeals From Interlocutory Orders",
                    "icon": None,
                    "document": "Rule-193.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XX. Practice Before the Court"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 200. Admission to Practice and Periodic Registration Fee",
                    "icon": None,
                    "document": "Rule-200(2nd-amended).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 201. Conduct of Practice Before the Court",
                    "icon": None,
                    "document": "Rule-201.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 202. Disciplinary Matters",
                    "icon": None,
                    "document": "Rule-202.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XXI. Declaratory Judgments"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 210. General",
                    "icon": None,
                    "document": "Rule-210_amended_08082024.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 211. Commencement of Action for Declaratory Judgment",
                    "icon": None,
                    "document": "Rule-211.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 212. Request for Place for Submission to the Court",
                    "icon": None,
                    "document": "Rule-212.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 213. Other Pleadings",
                    "icon": None,
                    "document": "Rule-213_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 214. Joinder of Issue in Action for Declaratory Judgment",
                    "icon": None,
                    "document": "Rule-214.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 215. Joinder of Parties",
                    "icon": None,
                    "document": "Rule-215.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 216. Intervention in Retirement Plan Actions",
                    "icon": None,
                    "document": "Rule-216.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 217. Disposition of Actions for Declaratory Judgment",
                    "icon": None,
                    "document": "Rule-217_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 218. Procedure in Actions Heard by a Special Trial Judge of the Court",
                    "icon": None,
                    "document": "Rule-218.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XXII. Disclosure Actions"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 220. General",
                    "icon": None,
                    "document": "Rule-220_amended_08082024.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 221. Commencement of Disclosure Action",
                    "icon": None,
                    "document": "Rule-221.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 222. Request for Place of Hearing",
                    "icon": None,
                    "document": "Rule-222.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 223. Other Pleadings",
                    "icon": None,
                    "document": "Rule-223.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 224. Joinder of Issue",
                    "icon": None,
                    "document": "Rule-224.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 225. Intervention",
                    "icon": None,
                    "document": "Rule-225.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 226. Joinder of Parties",
                    "icon": None,
                    "document": "Rule-226.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 227. Anonymous Parties",
                    "icon": None,
                    "document": "Rule-227.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 228. Confidentiality",
                    "icon": None,
                    "document": "Rule-228.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 229. Burden of Proof",
                    "icon": None,
                    "document": "Rule-229.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 229A. Procedure in Actions Heard by a Special Trial Judge of the Court",
                    "icon": None,
                    "document": "Rule-229A.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {
        "type": "h3",
        "value": "Title XXIII. Claims for Litigation and Administrative Costs",
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 230. General",
                    "icon": None,
                    "document": "Rule-230(2nd-amended).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 231. Claims for Litigation and Administrative Costs",
                    "icon": None,
                    "document": "Rule-231_Amended_03202023.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 232. Disposition of Claims for Litigation and Administrative Costs",
                    "icon": None,
                    "document": "Rule-232.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 233. Miscellaneous",
                    "icon": None,
                    "document": "Rule-233_Amended_03202023.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XXIV. TEFRA Partnership Actions"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 240. General",
                    "icon": None,
                    "document": "Rule-240_amended_08082024.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 241. Commencement of Partnership Action",
                    "icon": None,
                    "document": "Rule-241.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 242. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-242.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 243. Other Pleadings",
                    "icon": None,
                    "document": "Rule-243.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 244. Joinder of Issue in Partnership Action",
                    "icon": None,
                    "document": "Rule-244.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 245. Intervention and Participation",
                    "icon": None,
                    "document": "Rule-245.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 246. Service of Papers",
                    "icon": None,
                    "document": "Rule-246.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 247. Parties",
                    "icon": None,
                    "document": "Rule-247.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 248. Settlement Agreements",
                    "icon": None,
                    "document": "Rule-248.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 249. Action for Adjustment of Partnership Items Treated as Action for Readjustment of Partnership Items",
                    "icon": None,
                    "document": "Rule-249.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 250. Appointment and Removal of the Tax Matters Partner",
                    "icon": None,
                    "document": "Rule-250.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 251. Decisions",
                    "icon": None,
                    "document": "Rule-251.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XXIV.A. Partnership Actions Under BBA Section 1101"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 255.1. General",
                    "icon": None,
                    "document": "Rule-255.1_amended_08082024.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 255.2\t. Commencement of Partnership Action",
                    "icon": None,
                    "document": "Rule-255.2(New).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 255.3. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-255.3(New).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 255.4. Other Pleadings",
                    "icon": None,
                    "document": "Rule-255.4(New).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 255.5. Joinder of Issue in Partnership Action",
                    "icon": None,
                    "document": "Rule-255.5(New).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 255.6. Identification and Removal of Partnership Representative",
                    "icon": None,
                    "document": "Rule-255.6(New).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 255.7\t. Decisions",
                    "icon": None,
                    "document": "Rule-255.7(New).pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XXV. Supplemental Proceedings"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 260. Proceeding To Enforce Overpayment Determination",
                    "icon": None,
                    "document": "Rule-260(amended-Oct.-6,-2020).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 261. Proceeding To Redetermine Interest",
                    "icon": None,
                    "document": "Rule-261(amended-Oct.-6,-2020).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 262. Proceeding To Modify Decision in Estate Tax Case Involving Section 6166 Election",
                    "icon": None,
                    "document": "Rule-262(amended-Oct.-6,-2020).pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XXVI. Actions for Administrative Costs"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 270. General",
                    "icon": None,
                    "document": "Rule-270_amended_08082024.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 271. Commencement of Action for Administrative Costs",
                    "icon": None,
                    "document": "Rule-271.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 272. Other Pleadings",
                    "icon": None,
                    "document": "Rule-272.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 273. Joinder of Issue in Action for Administrative Costs",
                    "icon": None,
                    "document": "Rule-273.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 274. Applicable Small Tax Case Rules",
                    "icon": None,
                    "document": "Rule-274.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {
        "type": "h3",
        "value": "Title XXVII. Actions for Review of Failure To Abate Interest",
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 280. General",
                    "icon": None,
                    "document": "Rule-280_amended_08082024.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 281. Commencement of Action for Review of Failure To Abate Interest",
                    "icon": None,
                    "document": "Rule-281(amended).pdf",
                    "url": None,
                },
                {
                    "title": "Rule 282. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-282.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 283. Other Pleadings",
                    "icon": None,
                    "document": "Rule-283.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 284. Joinder of Issue in Action for Review of Failure To Abate Interest",
                    "icon": None,
                    "document": "Rule-284.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {
        "type": "h3",
        "value": "Title XXVIII. Actions for Redetermination of Employment Status",
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 290. General",
                    "icon": None,
                    "document": "Rule-290_amended_08082024.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 291. Commencement of Action for Redetermination of Employment Status",
                    "icon": None,
                    "document": "Rule-291.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 292. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-292.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 293. Other Pleadings",
                    "icon": None,
                    "document": "Rule-293.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 294. Joinder of Issue in Actions for Redetermination of Employment Status",
                    "icon": None,
                    "document": "Rule-294.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XXIX. Large Partnership Actions"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 300. General",
                    "icon": None,
                    "document": "Rule-300_amended_08082024.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 301. Commencement of Large Partnership Action",
                    "icon": None,
                    "document": "Rule-301.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 302. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-302.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 303. Other Pleadings",
                    "icon": None,
                    "document": "Rule-303.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 304. Joinder of Issue in Large Partnership Actions",
                    "icon": None,
                    "document": "Rule-304.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 305. Action for Adjustment of Partnership Items of Large Partnership Treated as Action for Readjustment of Partnership Items of Large Partnership",
                    "icon": None,
                    "document": "Rule-305.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {
        "type": "h3",
        "value": "Title XXX. Actions for Declaratory Judgment Relating to Treatment of Items Other Than Partnership Items With Respect to an Oversheltered Return",
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 310. General",
                    "icon": None,
                    "document": "Rule-310_amended_08082024.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 311. Commencement of Action for Declaratory Judgment (Oversheltered Return)",
                    "icon": None,
                    "document": "Rule-311.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 312. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-312.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 313. Other Pleadings",
                    "icon": None,
                    "document": "Rule-313.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 314. Joinder of Issue in Action for Declaratory Judgment (Oversheltered Return)",
                    "icon": None,
                    "document": "Rule-314.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 315. Disposition of Action for Declaratory Judgment (Oversheltered Return)",
                    "icon": None,
                    "document": "Rule-315.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 316. Action for Declaratory Judgment (Oversheltered Return) Treated as Deficiency Action",
                    "icon": None,
                    "document": "Rule-316.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {
        "type": "h3",
        "value": "Title XXXI. Actions for Determination of Relief From Joint and Several Liability on a Joint Return",
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 320. General",
                    "icon": None,
                    "document": "Rule-320.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 321. Commencement of Action for Determination of Relief From Joint and Several Liability on a Joint Return",
                    "icon": None,
                    "document": "Rule-321.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 322. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-322.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 323. Other Pleadings",
                    "icon": None,
                    "document": "Rule-323.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 324. Joinder of Issue in Action for Determination of Relief From Joint and Several Liability on a Joint Return",
                    "icon": None,
                    "document": "Rule-324.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 325. Notice and Intervention",
                    "icon": None,
                    "document": "Rule-325.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XXXII. Lien and Levy Actions"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 330. General",
                    "icon": None,
                    "document": "Rule-330.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 331. Commencement of Lien and Levy Action",
                    "icon": None,
                    "document": "Rule-331.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 332. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-332.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 333. Other Pleadings",
                    "icon": None,
                    "document": "Rule-333.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 334. Joinder of Issue in Lien and Levy Actions",
                    "icon": None,
                    "document": "Rule-334.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Title XXXIII. Whistleblower Actions"},
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 340. General",
                    "icon": None,
                    "document": "Rule-340.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 341. Commencement of Whistleblower Action",
                    "icon": None,
                    "document": "Rule-341.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 342. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-342.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 343. Other Pleadings",
                    "icon": None,
                    "document": "Rule-343.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 344. Joinder of Issue in Whistleblower Action",
                    "icon": None,
                    "document": "Rule-344.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 345. Privacy Protections for Filings in Whistleblower Actions",
                    "icon": None,
                    "document": "Rule-345.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {
        "type": "h3",
        "value": "Title XXXIV. Certification and Failure to Reverse Certification Action with Respect to Passports",
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Rule 350. General",
                    "icon": None,
                    "document": "Rule-350.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 351. Commencement of Certification Action",
                    "icon": None,
                    "document": "Rule-351.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 352. Request for Place of Trial",
                    "icon": None,
                    "document": "Rule-352.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 353. Other Pleadings",
                    "icon": None,
                    "document": "Rule-353.pdf",
                    "url": None,
                },
                {
                    "title": "Rule 354. Joinder of Issue in Certification Action",
                    "icon": None,
                    "document": "Rule-354.pdf",
                    "url": None,
                },
            ]
        },
    },
    {"type": "hr", "value": True},
    {"type": "h3", "value": "Appendix"},
    {
        "type": "paragraph",
        "value": 'The forms that comprise the appendix can also be found on the <a href="/case-related-forms">Case Related Forms</a> page.',
    },
    {
        "type": "links",
        "value": {
            "links": [
                {
                    "title": "Form 1. Petition (Sample Format)",
                    "icon": None,
                    "document": None,
                    "url": None,
                    "text_only": True,
                },
                {
                    "title": "Form 2. Petition (Simplified Form)",
                    "icon": None,
                    "document": "Petition_Simplified_Form_2.pdf",
                    "url": None,
                },
                {
                    "title": "Form 3. Petition for Administrative Costs",
                    "icon": None,
                    "document": "Petition_for_Administrative_Costs_Form_3.pdf",
                    "url": None,
                },
                {
                    "title": "Form 4. Statement of Taxpayer Identification Number",
                    "icon": None,
                    "document": "Form_4_Statement_of_Taxpayer_Identification_Number.pdf",
                    "url": None,
                },
                {
                    "title": "Form 5. Request for Place of Trial",
                    "icon": None,
                    "document": "Form_5_Request_for_Place_of_Trial.pdf",
                    "url": None,
                },
                {
                    "title": "Form 6. Corporate Disclosure Statement",
                    "icon": None,
                    "document": "Corporate_Disclosure_Statement_Form.pdf",
                    "url": None,
                },
                {
                    "title": "Form 7. Entry of Appearance",
                    "icon": None,
                    "document": "EOA_Form_7.pdf",
                    "url": None,
                },
                {
                    "title": "Form 8. Substitution of Counsel",
                    "icon": None,
                    "document": "SOC_Form_8.pdf",
                    "url": None,
                },
                {
                    "title": "Form 9. Certificate of Service",
                    "icon": None,
                    "document": "Certificate_of_Service_Form_-9.pdf",
                    "url": None,
                },
                {
                    "title": "Form 10. Notice of Change of Address",
                    "icon": None,
                    "document": "NOCOA_Form_10.pdf",
                    "url": None,
                },
                {
                    "title": "Form 11. Notice of Election to Intervene",
                    "icon": None,
                    "document": "Notice_of_Election_to_Intervene_Form_11.pdf",
                    "url": None,
                },
                {
                    "title": "Form 12. Notice of Election to Participate",
                    "icon": None,
                    "document": "Notice_of_Election_to_Participate_Form_12.pdf",
                    "url": None,
                },
                {
                    "title": "Form 13. Notice of Intervention",
                    "icon": None,
                    "document": "Notice_of_Intervention_Form_13.pdf",
                    "url": None,
                },
                {
                    "title": "Form 14A. Subpoena to Appear and Testify at a Hearing or Trial",
                    "icon": None,
                    "document": "Subpoena_Appear_Testify_Hearing_Or_Trial.pdf",
                    "url": None,
                },
                {
                    "title": "Form 14B. Subpoena to Testify at a Deposition",
                    "icon": None,
                    "document": "Subpoena_To_Testify_Deposition.pdf",
                    "url": None,
                },
                {
                    "title": "Form 15. Application for Order To Take Deposition To Perpetuate Evidence",
                    "icon": None,
                    "document": "AOTD_Form_15.pdf",
                    "url": None,
                },
                {
                    "title": "Form 16. Certificate on Return",
                    "icon": None,
                    "document": "Certificate_on_Return_of_Deposition_Form_16.pdf",
                    "url": None,
                },
                {
                    "title": "Form 17. Notice of Appeal to Court of Appeals",
                    "icon": None,
                    "document": "Notice_of_Appeal_Form_17.pdf",
                    "url": None,
                },
                {
                    "title": "Form 18. Unsworn Declaration Under Penalty of Perjury",
                    "icon": None,
                    "document": "Unsworn_Declaration_Form_18.pdf",
                    "url": None,
                },
            ]
        },
    },
]


class RulesPageInitializer(PageInitializer):
    def __init__(self):
        super().__init__()

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "rules"
        title = "Tax Court Rules"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"- {title} page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        for section in body:
            if section["type"] == "links" and "links" in section["value"]:
                for link in section["value"]["links"]:
                    if link["document"]:
                        uploaded_document = self.load_document_from_documents_dir(
                            subdirectory=None, filename=link["document"]
                        )
                        link["document"] = uploaded_document.id

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Rules of Practice and Procedure for the United States Tax Court",
                body=body,
            )
        )
        new_page.save_revision().publish()
        logger.info(f"Created the '{title}' page.")
