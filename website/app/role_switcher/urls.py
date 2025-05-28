from django.urls import path
from . import views

urlpatterns = [
    path("switch-role/", views.switch_role_view, name="switch_role"),
]
