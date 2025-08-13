from django.db import models
from django.contrib.auth import get_user_model
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.filters import WagtailFilterSet
import django_filters


class ExecuteScript(models.Model):
    command_name = models.CharField(
        max_length=255, help_text="Name of the command to execute", blank=False
    )

    EXECUTION_TYPE_CHOICES = [
        ("ONETIME", "One Time"),
        ("EVERYTIME", "Every Time"),
    ]

    execution_type = models.CharField(
        max_length=20,
        choices=EXECUTION_TYPE_CHOICES,
        default="ONETIME",
        help_text="How often this script should be executed",
    )

    datetime = models.DateTimeField(
        help_text="Date and time for script execution", blank=True, null=True
    )

    EXECUTION_STATUS_CHOICES = [
        ("success", "Success"),
        ("failure", "Failure"),
        ("pending", "Pending"),
    ]

    execution_status = models.CharField(
        max_length=20,
        choices=EXECUTION_STATUS_CHOICES,
        default="pending",
        help_text="Status of script execution",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_scripts",
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_scripts",
    )

    panels = [
        FieldPanel("command_name"),
        FieldPanel("execution_type"),
        FieldPanel("datetime"),
        FieldPanel("execution_status"),
    ]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.command_name


class ExecuteScriptFilterSet(WagtailFilterSet):
    execution_type = django_filters.ChoiceFilter(
        choices=ExecuteScript.EXECUTION_TYPE_CHOICES, label="Execution Type"
    )

    execution_status = django_filters.ChoiceFilter(
        choices=ExecuteScript.EXECUTION_STATUS_CHOICES, label="Execution Status"
    )

    class Meta:
        model = ExecuteScript
        fields = ["execution_type", "execution_status"]


class ExecuteScriptViewSet(SnippetViewSet):
    model = ExecuteScript
    list_display = [
        "command_name",
        "execution_type",
        "execution_status",
        "datetime",
        "created_at",
    ]
    filterset_class = ExecuteScriptFilterSet

    def user_has_permission(self, user, action):
        return user.is_superuser


register_snippet(ExecuteScript, viewset=ExecuteScriptViewSet)
