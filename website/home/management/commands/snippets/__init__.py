from home.management.commands.snippets.call_to_action_box import (
    CallToActionBoxInitializer,
)
from home.management.commands.snippets.navigation_ribbon import (
    NavigationRibbonInitializer,
)
from home.management.commands.snippets.new_navigation_ribbon import (
    NewNavigationRibbonInitializer,
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
    NewNavigationRibbonInitializer,
    ZoomgovProceedingRibbonInitializer,
    DawsonFAQsRibbonInitializer,
    ClinicsContactDetailsSnippetInitializer,
]

snippets_to_initialize_via_executescript = [
    CallToActionBoxInitializer,
]
