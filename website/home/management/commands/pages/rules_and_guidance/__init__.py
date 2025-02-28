from .administrative_orders_page import AdministrativeOrdersPageInitializer
from .clinics_pro_bono_page import ClinicsProBonoProgramsPageInitializer
from .getting_ready_page import GettingReadyPageInitializer
from .guidence_for_petitioners import GuidenceForPetitionersPageInitializer
from .guidence_for_practitioners_page import GuidenceForPractitionersPageInitializer
from .petitioners_about_page import PetitionersAboutInitializer
from .petitioners_after_trial_page import PetitionersAfterTrialInitializer
from .petitioners_before_trial_page import PetitionersBeforeTrialInitializer
from .petitioners_during_page import PetitionersDuringPageInitializer
from .petitioners_glossary_page import PetitionersGlossaryPageInitializer
from .petitioners_start_page import PetitionersStartPageInitializer
from .remote_basics import RemoteBasicsPageInitializer
from .remote_proceedings_page import RemoteProceedingsPageInitializer
from .zoomgov_proceedings_page import ZoomgovProceedingPageInitializer
from .judicial_conduct_and_disability_procedures_page import (
    JudicialConductAndDisabilityProceduresPageInitializer,
)
from .rules_page import RulesPageInitializer

rules_and_guidance_pages_to_initialize = [
    RemoteProceedingsPageInitializer,
    GuidenceForPetitionersPageInitializer,
    AdministrativeOrdersPageInitializer,
    PetitionersStartPageInitializer,
    PetitionersAboutInitializer,
    PetitionersDuringPageInitializer,
    PetitionersBeforeTrialInitializer,
    PetitionersAfterTrialInitializer,
    PetitionersBeforeTrialInitializer,
    PetitionersGlossaryPageInitializer,
    RemoteBasicsPageInitializer,
    ZoomgovProceedingPageInitializer,
    ClinicsProBonoProgramsPageInitializer,
    GuidenceForPractitionersPageInitializer,
    GettingReadyPageInitializer,
    JudicialConductAndDisabilityProceduresPageInitializer,
    RulesPageInitializer,
]
