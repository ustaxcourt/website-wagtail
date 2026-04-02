from django.urls import path
from chatbot import views

urlpatterns = [
    path("ask/", views.ask, name="chatbot_ask"),
    path(
        "generate-alt-text/", views.generate_alt_text, name="chatbot_generate_alt_text"
    ),
]
