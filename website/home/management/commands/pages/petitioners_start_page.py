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
            name="Blue Navigation Bar"
        ).first()

        questions = [
            {
                "question": "What does it mean that the Tax Court is a court of limited jurisdiction?",
                "answer": "The United States Tax Court is a court of limited jurisdiction. As a general rule, you must wait until the IRS takes action (for example, sends you a Notice of Deficiency or a Notice of Determination) or fails to take an action before you can file a petition in the Tax Court. Most cases begin when the IRS issues a Notice of Deficiency, which gives you the right to challenge the IRS in the Tax Court by filing a petition within the time provided by law.",
            },
            {
                "question": "How do I begin a case in the Tax Court?",
                "answer": 'To begin a case, you must file a petition with the Tax Court. The first step is ensuring that you have a valid notice from the IRS (such as a Notice of Deficiency or a Notice of Determination), or that you otherwise meet the specific requirements that allow you to file. The Court cannot extend the time for filing, as that time is set by statute. Always check your IRS notice or the <a href="https://www.ustaxcourt.gov/">Tax Court’s website</a> for guidance about the deadline.',
            },
            {
                "question": "What should my petition include?",
                "answer": 'Your petition should include:<br><br>- Your name and address (along with telephone number and email if you are not represented by counsel).<br>- The year(s) or period(s) for which the IRS made its determination.<br>- The city where you want your trial. A list of the Court’s trial locations is on the <a href="https://www.ustaxcourt.gov/">Tax Court’s website</a>.<br>- A clear and concise assignment of each and every error you believe the IRS made.<br>- A clear and concise statement of the facts on which you base your assignments of error.<br><br>More details are available in the Tax Court Rules of Practice and Procedure.',
            },
            {
                "question": "Do I need to attach anything to my petition?",
                "answer": "If you are filing your petition in response to a Notice of Deficiency, Notice of Determination, or similar IRS notice, attach a copy of that notice to your petition. This helps the Court identify the type of case and verify that your petition is timely.",
            },
            {
                "question": "Can I use the Court’s forms to file my petition?",
                "answer": 'Yes. The Court provides petition forms that you can use. These forms are available in both electronic fillable format and PDF on the Court’s <a href="https://www.ustaxcourt.gov/forms.html">Forms page</a>. If you choose to create your own petition, be sure to follow the Court’s Rules of Practice and Procedure.',
            },
            {
                "question": "What if I do not have a notice from the IRS?",
                "answer": "If you have not received a Notice of Deficiency, Notice of Determination, or another type of IRS notice that gives you the right to file a petition, you may not be eligible to file a Tax Court case yet. The Court cannot provide legal advice, so if you are unsure about your right to file a petition, you should consult an attorney or a qualified tax professional.",
            },
            {
                "question": "How much does it cost to file a petition?",
                "answer": "The fee to file a petition is $If you file your petition electronically, you may pay online. If you file a paper petition, you can pay by check, money order, or other draft, payable to “Clerk, United States Tax Court.”",
            },
            {
                "question": "What if I cannot afford the filing fee?",
                "answer": 'If you are unable to pay the $filing fee, you may file an <em>Application for Waiver of Filing Fee</em> at the same time you file your petition. The application form is available on the Court’s <a href="https://www.ustaxcourt.gov/forms.html">Forms page</a> under “Administrative and Procedural Forms.” If the Court denies your application, you will be required to pay the fee or your case may be dismissed.',
            },
            {
                "question": "Who needs to sign the petition?",
                "answer": "If you are filing a petition on your own, you must sign it yourself. If you and your spouse are filing a joint petition, you must both sign. If you are represented by an attorney, your attorney can sign on your behalf, but you must comply with the Court’s rules regarding representation.",
            },
            {
                "question": "What is the deadline to file my petition?",
                "answer": "The deadline to file a petition depends on the type of notice you received from the IRS. The Notice of Deficiency, for example, typically gives you days (150 days if the notice is addressed to you outside the United States) to file a petition. You must file on or before the last date indicated in your IRS notice. The Court cannot extend this deadline.",
            },
            {
                "question": "What if the last date to file falls on a weekend or holiday?",
                "answer": 'If the last date for filing a petition falls on a Saturday, Sunday, or legal holiday in the District of Columbia, the petition will be timely if it is delivered to the Court or properly addressed, postage prepaid, and mailed (or sent by an approved delivery service) on the next day that is not a Saturday, Sunday, or legal holiday. For more information, see <a href="https://www.ustaxcourt.gov/rules.html">Rule 25</a> of the Tax Court Rules of Practice and Procedure.',
            },
            {
                "question": "How does the ‘timely mailed = timely filed’ rule work?",
                "answer": "If you mail your petition to the Court, the postmark date on the envelope will be used to determine if you filed your petition on time. If you use a private delivery service designated by the IRS, the date recorded by that service is treated as the postmark date. Make sure the petition is properly addressed, has sufficient postage, and is postmarked on or before the deadline.",
            },
            {
                "question": "Where should I send my petition?",
                "answer": 'You can mail or deliver your petition to the U.S. Tax Court at:<br><br>United States Tax Court<br>2nd Street, N.W.<br>Washington, D.C. 20217<br><br>If you mail the petition, it is considered filed on the postmark date, provided it meets the requirements in <a href="https://www.ustaxcourt.gov/rules.html">Rule 25</a>. If filing electronically, you must use the Court’s <a href="https://dawson.ustaxcourt.gov">DAWSON system</a>.',
            },
            {
                "question": "What is the Court’s DAWSON system?",
                "answer": 'DAWSON is the Tax Court’s electronic case management system. You can file most documents electronically, including your petition, through <a href="https://dawson.ustaxcourt.gov">DAWSON</a>. You must register for an account and follow the instructions on the site for filing documents electronically.',
            },
            {
                "question": "Should I keep my contact information updated with the Court?",
                "answer": "Yes. You are required to keep the Court informed of your current address, phone number, and email address. If you do not provide updated contact information, you risk missing important Court notices or deadlines, which could adversely affect your case.",
            },
            {
                "question": "What happens after I file my petition?",
                "answer": "After you file your petition, the Tax Court will mail you a Notice of Receipt of Petition. This notice is the official acknowledgment that your case has been filed. The Court will then serve a copy of your petition on the IRS, and the IRS typically has days from the date of service to file its answer or a motion.",
            },
            {
                "question": "What is a Notice of Receipt of Petition?",
                "answer": "A Notice of Receipt of Petition is a document the Tax Court sends to you to confirm that it has received and filed your petition. Keep it with your records, as it contains your docket number and other important information about your case.",
            },
            {
                "question": "What is ‘service of papers’ according to Rule 21?",
                "answer": '‘Service of papers’ means delivering documents filed in the case to the other party (or that party’s counsel). When you file a document with the Court, you must also serve it on the other party, typically by mail or through electronic means if both parties have consented to electronic service. For more information, see <a href="https://www.ustaxcourt.gov/rules.html">Rule 21</a> of the Tax Court Rules of Practice and Procedure.',
            },
            {
                "question": "What is an answer from the IRS?",
                "answer": 'The IRS’s answer is a written response to your petition. It generally admits or denies the statements you made in your petition. The IRS usually has days from the date the Court serves your petition to file its answer (unless the Court grants additional time). If the IRS raises new issues in its answer, you may need to file a reply. For more information, see <a href="https://www.ustaxcourt.gov/rules.html">Rule 36</a> of the Tax Court Rules.',
            },
            {
                "question": "What if the IRS denies my allegations in its answer?",
                "answer": "If the IRS denies your allegations, you will have to prove them at trial. You should be prepared to provide evidence and testimony to support your position. The Rules of Evidence apply in Tax Court, subject to certain exceptions for small tax cases (S cases).",
            },
            {
                "question": "What if the IRS raises new issues in its answer?",
                "answer": 'If the IRS introduces new issues in its answer (issues not addressed in your petition), you generally must file a reply. If you do not, the new issues are deemed denied. A reply is your written response to those new issues. Refer to <a href="https://www.ustaxcourt.gov/rules.html">Rule 36</a> for more information on how and when to file a reply.',
            },
            {
                "question": "What is a small tax case (S case), and how is it different from a regular tax case?",
                "answer": "A small tax case, often referred to as an S case, is a simplified procedure available if the amount of tax in dispute is $50,or less for each year at issue. The rules are less formal, and trials are generally shorter. However, decisions in S cases are final and cannot be appealed. Regular cases follow more formal procedures and may be appealed to a U.S. Court of Appeals.",
            },
            {
                "question": "Can I change my case from a small tax case to a regular tax case?",
                "answer": "Yes. You may make a motion to remove the small tax case designation before the trial begins if you decide you want to proceed as a regular case. However, once the trial has started, it may be too late to switch. The IRS can also ask the Court to remove the S case designation in certain circumstances.",
            },
            {
                "question": "How does filing a petition affect IRS enforcement actions?",
                "answer": "Generally, when you file a petition in response to a Notice of Deficiency, the IRS is barred from assessing or collecting the tax while the case is pending. However, there may be exceptions for certain types of taxes or penalties. For other enforcement actions—such as a levy or lien—the effect of filing may vary. Check your specific IRS notice or consult an attorney to understand the impact on enforcement for your situation.",
            },
            {
                "question": "Will I get a trial date after I file my petition?",
                "answer": "Yes. Once the IRS files its answer (or once the pleadings are otherwise complete), the Court will eventually issue a Notice Setting Case for Trial. This notice will tell you the date, time, and location of your trial session. Cases are scheduled for trial sessions around the country in approximately cities.",
            },
            {
                "question": "What if I can’t attend on the scheduled trial date?",
                "answer": "If you are unable to attend on the scheduled date, you can file a motion for continuance (postponement) with the Court. You should file this motion as soon as possible and explain why you need a continuance. The Court will consider your motion and may grant or deny it. If the Court denies it, you must be prepared to appear on the scheduled date or risk dismissal of your case.",
            },
            {
                "question": "Can I ask the Court for a continuance on the day of trial?",
                "answer": "You may file a motion for continuance even close to the trial date, but the Court is less likely to grant it unless you have a very good reason (such as a serious medical issue). It is always best to request a continuance as soon as you know you need one. Last-minute requests may be denied.",
            },
            {
                "question": "What happens if I do not appear for trial?",
                "answer": "If you fail to appear at trial, the Court may dismiss your case for lack of prosecution, meaning you lose by default. If your case is dismissed, the IRS’s determination is generally upheld. It is very important to appear on your trial date or to arrange for a continuance if you have a conflict.",
            },
            {
                "question": "What is a Notice Setting Case for Trial?",
                "answer": "A Notice Setting Case for Trial is an order the Court sends you after the IRS has filed its answer and your case is ready for scheduling. It provides the date, time, and place of the trial session in which your case will be heard. Be sure to read it carefully and note any deadlines for exchanging information or filing pretrial documents.",
            },
            {
                "question": "What are proposed stipulations of fact?",
                "answer": 'Before trial, you and the IRS should work together to agree on facts that are not in dispute. These agreed facts are placed in a written stipulation, which helps the Court and saves time at trial. For more information, see <a href="https://www.ustaxcourt.gov/rules.html">Rule 91</a> of the Tax Court Rules of Practice and Procedure.',
            },
            {
                "question": "Why is stipulating facts important?",
                "answer": "Stipulating facts (reaching agreement on certain factual issues) allows you and the IRS to focus on the genuinely disputed issues at trial. It streamlines the process and helps the Court understand the core arguments in the case. Failure to stipulate may result in the Court’s disfavor or additional trial complexities.",
            },
            {
                "question": "What is ‘discovery’ in Tax Court, and do I need to exchange information with the IRS?",
                "answer": 'Discovery is the process by which parties exchange information before trial. In the Tax Court, both you and the IRS are required to provide relevant information and documents. For more details, see <a href="https://www.ustaxcourt.gov/rules.html">Rules 70–74</a> of the Tax Court Rules of Practice and Procedure.',
            },
            {
                "question": "How do I exchange documents and evidence with the IRS?",
                "answer": "You must provide copies of any documents you plan to use as evidence to the IRS before trial. Likewise, the IRS must provide you with copies of documents it plans to use. If either party fails to exchange documents, the Court may exclude those documents at trial. Always comply with the pretrial order and discovery rules (Rules 70–74).",
            },
            {
                "question": "What if I need a witness or documents from someone who is not a party to the case?",
                "answer": 'You can ask the Court to issue a subpoena to require a third party to appear as a witness or produce documents for trial. Subpoenas must be issued in accordance with <a href="https://www.ustaxcourt.gov/rules.html">Rule 147</a> of the Tax Court Rules, and you must serve the subpoena properly. Keep in mind that there may be fees or mileage costs associated with subpoenaing a witness.',
            },
            {
                "question": "Can I settle my case with the IRS before trial?",
                "answer": "Yes. Many cases are settled without going to trial. You and the IRS can discuss settlement at any time before or during the trial. If you reach an agreement, it will be memorialized in a settlement document, and the Court will enter a decision based on that settlement.",
            },
            {
                "question": "What if I want to talk to the IRS about settling or narrowing the issues?",
                "answer": "You can contact the IRS attorney or Appeals Officer assigned to your case to discuss settlement or narrowing the issues. The Court encourages the parties to communicate and attempt to resolve the case or simplify the issues before trial.",
            },
            {
                "question": "Can I represent myself in Tax Court?",
                "answer": "Yes. Most taxpayers represent themselves, which is called proceeding <em>pro se</em>. However, you also have the right to be represented by someone admitted to practice before the Tax Court. If you choose to represent yourself, be sure to familiarize yourself with the Court’s Rules and procedures.",
            },
            {
                "question": "Can a non-attorney represent me in the Tax Court?",
                "answer": 'In certain circumstances, non-attorney practitioners (such as enrolled agents) may be admitted to practice before the Tax Court if they meet specific requirements. You can learn more by visiting the <a href="https://www.ustaxcourt.gov/practitioners.html">Practitioners page</a> on the Court’s website. If you do not hire an attorney or qualified practitioner, you will generally have to represent yourself.',
            },
            {
                "question": "What is limited appearance representation?",
                "answer": "An attorney admitted to practice before the Tax Court can enter a limited appearance on your behalf—often just for a trial session or a particular motion. This allows you to receive help with specific parts of your case without retaining the attorney for the entire proceeding. The attorney will file a Limited Entry of Appearance form with the Court.",
            },
            {
                "question": "What if I cannot afford to hire an attorney?",
                "answer": 'If you cannot afford an attorney, you may qualify for help from a Low Income Taxpayer Clinic (LITC). These clinics are independent from the IRS and the Tax Court, and they provide free or low-cost representation to qualifying individuals. Information about LITCs is available on the <a href="https://www.taxpayeradvocate.irs.gov/litc/">IRS’s LITC page</a>. You can also find resources on the Court’s website.',
            },
            {
                "question": "What if I want to withdraw my petition or end my case before trial?",
                "answer": "If you decide you no longer wish to pursue your case, you can file a motion to dismiss. The Court will consider your request, and if granted, the IRS’s determination may become final. However, if you have a settlement, the better option is often to file a stipulated decision with the IRS to reflect your agreement.",
            },
            {
                "question": "What happens at the trial?",
                "answer": "At trial, both parties present their evidence and arguments. You will have the opportunity to testify, present documents, call witnesses, and cross-examine IRS witnesses. The trial is conducted before a Tax Court judge (or, in some small tax cases, a special trial judge).",
            },
            {
                "question": "Do I receive a decision right after the trial?",
                "answer": "Not always. In many cases, the judge will take the case under advisement and issue a written opinion or decision at a later date. Sometimes, in simpler cases or small tax cases, the judge may announce a decision from the bench.",
            },
            {
                "question": "What if I disagree with the Tax Court’s final decision?",
                "answer": "If your case is a regular tax case, you generally have the right to appeal the final decision to the U.S. Court of Appeals for the circuit in which you reside (or the Federal Circuit, depending on the issue). If your case is a small tax case (S case), the decision cannot be appealed. Be sure to check the rules and deadlines for filing an appeal.",
            },
            {
                "question": "Do I need to keep copies of everything I file with the Court?",
                "answer": "Yes. Always keep copies of all documents you file with the Court and any documents the Court or IRS sends to you. You’ll need these documents to prepare for trial and to respond to any motions or Court orders. It’s best to organize them in a way that allows you to quickly find what you need.",
            },
            {
                "question": "Where can I find the Tax Court’s Rules of Practice and Procedure?",
                "answer": 'You can find the Court’s Rules of Practice and Procedure on the Court’s official website at <a href="https://www.ustaxcourt.gov/rules.html">https://www.ustaxcourt.gov/rules.html</a>. It is important to review these rules to understand the requirements and deadlines that apply to your case. The website also has forms, guides, and other resources that can help you navigate the process.',
            },
        ]

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                navigation_ribbon=navigation_ribbon,
                search_description="Resources about the Court's Zoomgov remote proceedings",
                body=[
                    {"type": "heading", "value": "Starting A Case"},
                    {"type": "hr", "value": True},
                    {
                        "type": "paragraph",
                        "value": "This guide provides information, but not legal advice, for individuals who represent themselves before the Tax Court. It answers some of taxpayers' most frequent questions. It is a brief step-by-step explanation of the process of:",
                    },
                    {"type": "hr", "value": True},
                    {
                        "type": "questionanswers",
                        "value": {"questionanswers": questions},
                    },
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
