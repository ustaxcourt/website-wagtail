import logging
import os
from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from home.models import (
    CaseRelatedFormsPage,
    CaseRelatedFormsEntry,
)
from django.core.files import File
from wagtail.documents import get_document_model
from home.management.commands.pages.page_initializer import PageInitializer
from home.models import NavigationCategories

logger = logging.getLogger(__name__)

forms_data = [
    {
        "formName": "Application for Order to Take Deposition to Perpetuate Evidence",
        "formNameNote": "",
        "number": "Form 15",
        "eligibleForEFilingByPetitioners": "Yes",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "AOTD_Form_15.pdf",
    },
    {
        "formName": "Application for Waiver of Filing Fee",
        "formNameNote": "",
        "number": "",
        "eligibleForEFilingByPetitioners": "Yes, if not filed with the petition",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Application_for_Waiver_of_Filing_Fee.pdf",
    },
    {
        "formName": "Certificate of Service",
        "formNameNote": "",
        "number": "Form 9",
        "eligibleForEFilingByPetitioners": "Yes",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Certificate_of_Service_Form_-9.pdf",
    },
    {
        "formName": "Certificate on Return of Deposition",
        "formNameNote": "",
        "number": "Form 16",
        "eligibleForEFilingByPetitioners": "No",
        "eligibleForEFilingByPractitioners": "No",
        "pdf_filename": "Certificate_on_Return_of_Deposition_Form_16.pdf",
    },
    {
        "formName": "Corporate Disclosure Statement",
        "formNameNote": "",
        "number": "Form 6",
        "eligibleForEFilingByPetitioners": "Yes",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Corporate_Disclosure_Statement_Form.pdf",
    },
    {
        "formName": "Entry of Appearance",
        "formNameNote": "",
        "number": "Form 7",
        "eligibleForEFilingByPetitioners": "N/A",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "EOA_Form_7.pdf",
    },
    {
        "formName": "Limited Entry of Appearance",
        "formNameNote": "",
        "number": "",
        "eligibleForEFilingByPetitioners": "N/A",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Limited_Entry_of_Appearance.pdf",
    },
    {
        "formName": "Motion To Proceed Remotely",
        "formNameNote": "",
        "number": "",
        "eligibleForEFilingByPetitioners": "Yes",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Motion_to_Proceed_Remotely.pdf",
    },
    {
        "formName": "Notice of Appeal to Court of Appeals",
        "formNameNote": "",
        "number": "Form 17",
        "eligibleForEFilingByPetitioners": "Yes",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Notice_of_Appeal_Form_17.pdf",
    },
    {
        "formName": "Notice of Change of Address",
        "formNameNote": "",
        "number": "Form 10",
        "eligibleForEFilingByPetitioners": "No",
        "eligibleForEFilingByPractitioners": "No",
        "pdf_filename": "NOCOA_Form_10.pdf",
    },
    {
        "formName": "Notice of Completion",
        "formNameNote": "",
        "number": "",
        "eligibleForEFilingByPetitioners": "N/A",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Notice_of_Completion_LEA.pdf",
    },
    {
        "formName": "Notice of Election to Intervene",
        "formNameNote": "",
        "number": "Form 11",
        "eligibleForEFilingByPetitioners": "No",
        "eligibleForEFilingByPractitioners": "No",
        "pdf_filename": "Notice_of_Election_to_Intervene_Form_11.pdf",
    },
    {
        "formName": "Notice of Election to Participate",
        "formNameNote": "",
        "number": "Form 12",
        "eligibleForEFilingByPetitioners": "No",
        "eligibleForEFilingByPractitioners": "No",
        "pdf_filename": "Notice_of_Election_to_Participate_Form_12.pdf",
    },
    {
        "formName": "Notice of Intervention",
        "formNameNote": "",
        "number": "Form 13",
        "eligibleForEFilingByPetitioners": "No",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Notice_of_Intervention_Form_13.pdf",
    },
    {
        "formName": "Petition Kit",
        "formNameNote": "(contains all forms needed to file a case)",
        "number": "Forms 2, 4 & 5",
        "eligibleForEFilingByPetitioners": "Yes",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Petition_Kit.pdf",
    },
    {
        "formName": "Petition",
        "formNameNote": "(Simplified Form)",
        "number": "Form 2",
        "eligibleForEFilingByPetitioners": "Yes",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Petition_Simplified_Form_2.pdf",
    },
    {
        "formName": "Petition for Administrative Costs",
        "formNameNote": "",
        "number": "Form 3",
        "eligibleForEFilingByPetitioners": "No",
        "eligibleForEFilingByPractitioners": "No",
        "pdf_filename": "Petition_for_Administrative_Costs_Form_3.pdf",
    },
    {
        "formName": "Pre-Trial Memorandum",
        "formNameNote": "",
        "number": "",
        "eligibleForEFilingByPetitioners": "Yes",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Pretrial_Memorandum_Form.pdf",
    },
    {
        "formName": "Request for Place of Trial",
        "formNameNote": "",
        "number": "Form 5",
        "eligibleForEFilingByPetitioners": "Yes, if not filed with the petition",
        "eligibleForEFilingByPractitioners": "Yes, if not filed with the petition",
        "pdf_filename": "Form_5_Request_for_Place_of_Trial.pdf",
    },
    {
        "formName": "Statement of Taxpayer Identification Number",
        "formNameNote": "",
        "number": "Form 4",
        "eligibleForEFilingByPetitioners": "No",
        "eligibleForEFilingByPractitioners": "No",
        "pdf_filename": "Form_4_Statement_of_Taxpayer_Identification_Number.pdf",
    },
    {
        "formName": "Subpoena to Appear and Testify at a Hearing or Trial",
        "formNameNote": "",
        "number": "Form 14A",
        "eligibleForEFilingByPetitioners": "N/A",
        "eligibleForEFilingByPractitioners": "N/A",
        "pdf_filename": "Subpoena_Appear_Testify_Hearing_Or_Trial.pdf",
    },
    {
        "formName": "Subpoena to Testify at a Deposition",
        "formNameNote": "",
        "number": "Form 14B",
        "eligibleForEFilingByPetitioners": "N/A",
        "eligibleForEFilingByPractitioners": "N/A",
        "pdf_filename": "Subpoena_To_Testify_Deposition.pdf",
    },
    {
        "formName": "Substitution of Counsel",
        "formNameNote": "",
        "number": "Form 8",
        "eligibleForEFilingByPetitioners": "N/A",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "SOC_Form_8.pdf",
    },
    {
        "formName": "Unsworn Declaration Under Penalty of Perjury",
        "formNameNote": "",
        "number": "Form 18",
        "eligibleForEFilingByPetitioners": "Yes",
        "eligibleForEFilingByPractitioners": "Yes",
        "pdf_filename": "Unsworn_Declaration_Form_18.pdf",
    },
]


class CaseRelatedFormPageInitializer(PageInitializer):
    def create(self):
        try:
            home_page = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            logger.error("Home page does not exist.")
            return

        self.create_page_info(home_page)

        for form in forms_data:
            self.create_form_entry(form)

    def create_page_info(self, home_page):
        slug = "case_related_forms"
        title = "Case Related Forms"

        if Page.objects.filter(slug=slug).exists():
            logger.info(f"'{title}' page already exists.")
            return

        logger.info(f"Creating the '{title}' page.")

        content_type = ContentType.objects.get_for_model(CaseRelatedFormsPage)

        new_page = home_page.add_child(
            instance=CaseRelatedFormsPage(
                title=title,
                body='Forms can be filled in and printed directly from <a href="https://acrobat.adobe.com/us/en/acrobat/pdf-reader.html" target="_blank">Adobe Acrobat Reader</a> 3.0 or later. For assistance, see the <a href="https://ustaxcourt.gov/forms_instructions.html">Fill-in Forms Instructions</a>.',
                slug=slug,
                seo_title=title,
                search_description="Case Related Forms",
                content_type=content_type,
                show_in_menus=True,
            )
        )

        CaseRelatedFormsPage.objects.filter(id=new_page.id).update(
            menu_item_name="CASE RELATED FORMS",
            navigation_category=NavigationCategories.eFILING_AND_CASE_MAINTENANCE,
        )

        logger.info(f"Successfully created the '{title}' page.")

    def create_form_entry(self, formData):
        try:
            parent_page = CaseRelatedFormsPage.objects.get(slug="case_related_forms")
        except CaseRelatedFormsPage.DoesNotExist:
            logger.error("Parent page 'Case Related Forms' does not exist.")
            return

        # Check if the form already exists
        if CaseRelatedFormsEntry.objects.filter(formName=formData["formName"]).exists():
            logger.info(f"Form entry for {formData['formName']} already exists.")
            return

        pdf_path = (
            f'home/management/documents/case_related_forms/{formData["pdf_filename"]}'
        )

        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found at {pdf_path}.")
            return

        Document = get_document_model()

        # Create the form record
        with open(pdf_path, "rb") as pdf_file:
            document = Document(
                title=formData["formName"],
                file=File(pdf_file, name=os.path.basename(pdf_path)),
            )
            document.save()

            form = CaseRelatedFormsEntry(
                formName=formData["formName"],
                formNameNote=formData["formNameNote"],
                number=formData["number"],
                eligibleForEFilingByPetitioners=formData[
                    "eligibleForEFilingByPetitioners"
                ],
                eligibleForEFilingByPractitioners=formData[
                    "eligibleForEFilingByPractitioners"
                ],
                pdf=document,
                parentpage=parent_page,  # Use parentpage directly, not parentpage_id
            )
            form.save()  # Just save the model directly

        logger.info(f"Successfully created form entry: {formData['formName']}")
