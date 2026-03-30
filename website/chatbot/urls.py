from django.urls import path
from chatbot import views

urlpatterns = [
    path("ask/", views.ask, name="chatbot_ask"),
]
