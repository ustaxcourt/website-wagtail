from home.models import CommonText
import logging

logger = logging.getLogger(__name__)


class ClinicsContactDetailsSnippetInitializer:
    def __init__(self):
        self.logger = logger
        self.name = "Clinics Contact Details"

    def create(self):
        if CommonText.objects.filter(name=self.name).exists():
            logger.info(f"{self.name} already exists.")
            return

        logger.info(f"Creating the snippet {self.name}.")

        clinics_contact_details = CommonText(
            name=self.name,
            text="""Please <a href="mailto:litc@ustaxcourt.gov" title="email: litc@ustaxcourt.gov">contact us</a> with any questions concerning the Court’s program or requirements, or call <a href="tel:202-521-3366" title="call: 202-521-3366">202-521-3366</a>.""",
        )

        clinics_contact_details.save()
