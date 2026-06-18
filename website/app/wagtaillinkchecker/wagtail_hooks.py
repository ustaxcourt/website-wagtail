from __future__ import unicode_literals

from django.utils.translation import gettext_lazy as _

from . import urls
from django.urls import reverse
from wagtail.admin.menu import MenuItem
from wagtail import hooks


@hooks.register("register_admin_urls")
def register_admin_urls():
    return urls.urlpatterns


@hooks.register("register_settings_menu_item")
def register_menu_settings():
    return MenuItem(
        _("Link Checker"),
        reverse("wagtaillinkchecker"),
        icon_name="link",
        order=300,
    )
