from wagtail.models import Page
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import EnhancedStandardPage

jcdp_docs = {
    "jcd_rules.pdf": "",
    "jcd_users_guide.pdf": "",
    "jcd_complaint_form.pdf": "",
}


class JudicialConductAndDisabilityProceduresPageInitializer(PageInitializer):
    def __init__(self, logger):
        super().__init__(logger)

    def create(self):
        home_page = Page.objects.get(slug="home")
        self.create_page_info(home_page)

    def create_page_info(self, home_page):
        slug = "jcdp"
        title = "Judicial Conduct and Disability Procedures"

        if Page.objects.filter(slug=slug).exists():
            self.logger.write(f"- {title} page already exists.")
            return

        self.logger.write(f"Creating the '{title}' page.")

        for document in jcdp_docs.keys():
            uploaded_document = self.load_document_from_documents_dir("jcdp", document)
            jcdp_docs[document] = uploaded_document.file.url

        body_text = (
            "<p>Congress has created a procedure that permits any person to file a complaint about the behavior of Federal judges, including Tax Court judges.</p>"
            "<p>The law says that complaints about judges' decisions and complaints with no evidence to support them must be dismissed. Thus, if you are a litigant in a case, even if you believe the judge made a wrong decision you may not use this procedure to object to the decision.</p>"
            f"""<p>Below are Links to the Procedures that establish what may be complained about, who may be complained about, where to file a complaint, and how the complaint will be processed. You may view the <strong><a href="{jcdp_docs["jcd_rules.pdf"]}" target="_blank" title="Tax Court Judicial Conduct and Judicial Disability Procedures">Tax Court Judicial Conduct and Judicial Disability Procedures</a></strong>, a <strong><a href="{jcdp_docs["jcd_users_guide.pdf"]}" target="_blank" title="User’s Guide to the Judicial Conduct and Judicial Disability Procedures">User’s Guide to the Judicial Conduct and Judicial Disability Procedures</a></strong>, and <strong><a href="/jcdp_orders_issued" title="Orders issued in Judicial Conduct and Disability Cases">Orders issued in Judicial Conduct and Disability Cases in the Tax Court</a></strong>. You must submit any complaints on the <strong><a href="{jcdp_docs["jcd_complaint_form.pdf"]}" target="_blank" title="Complaint form">complaint form</a></strong>. You may complete the form online, print it, and mail it to the address indicated in both the Procedures and the Users’ Guide. The form may not be submitted electronically.</p>"""
        )

        new_page = home_page.add_child(
            instance=EnhancedStandardPage(
                title=title,
                slug=slug,
                seo_title=title,
                search_description="Judicial Conduct And Disability Procedures",
                body=[
                    {"type": "paragraph", "value": body_text},
                ],
                show_in_menus=False,
            )
        )
        new_page.save_revision().publish()
        self.logger.write(f"Created the '{title}' page.")
