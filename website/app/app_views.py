# app/auth_views.py

from django.views.decorators.cache import never_cache
from social_django import views as social_views

# Create decorated, "never_cache" versions of the social_django views.
# We are simply wrapping the original library views with the decorator.
auth = never_cache(social_views.auth)
complete = never_cache(social_views.complete)
disconnect = never_cache(social_views.disconnect)
