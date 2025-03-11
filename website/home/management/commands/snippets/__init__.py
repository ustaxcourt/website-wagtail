from home.management.commands.snippets.navigation_ribbon import (
    NavigationRibbonInitializer,
)
from home.management.commands.snippets.zoomgov_proceeding_ribbon import (
    ZoomgovProceedingRibbonInitializer,
)
from home.management.commands.snippets.dawson_faqs_ribbon import (
    DawsonFAQsRibbonInitializer,
)

from home.management.commands.snippets.clinics_contact_details_snippet import (
    ClinicsContactDetailsSnippetInitializer,
)

snippets_to_initialize = [
    NavigationRibbonInitializer,
    ZoomgovProceedingRibbonInitializer,
    DawsonFAQsRibbonInitializer,
    ClinicsContactDetailsSnippetInitializer,
]
