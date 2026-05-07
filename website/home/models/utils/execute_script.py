from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
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
        ("SUCCESS", "Success"),
        ("FAILURE", "Failure"),
        ("PENDING", "Pending"),
    ]

    execution_status = models.CharField(
        max_length=20,
        choices=EXECUTION_STATUS_CHOICES,
        default="PENDING",
        help_text="Status of script execution",
    )

    execution_log = RichTextField(
        blank=True,
        help_text="Rich text log of script execution output and details",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_scripts",
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_scripts",
        blank=True,
    )

    panels = [
        FieldPanel("command_name"),
        FieldPanel("execution_type"),
        FieldPanel("datetime"),
        FieldPanel("execution_status"),
        FieldPanel("execution_log"),
    ]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.command_name

    @classmethod
    def command_exists(cls, command_name, execution_type="ONETIME"):
        """
        Check if a script with the given command_name and execution_type already exists.
        """
        valid_types = [choice[0] for choice in cls.EXECUTION_TYPE_CHOICES]
        if execution_type is not None and execution_type not in valid_types:
            raise ValueError(
                f"execution_type must be one of {valid_types}, got '{execution_type}'"
            )

        queryset = cls.objects.filter(command_name=command_name)
        if execution_type is not None:
            queryset = queryset.filter(execution_type=execution_type)
        return queryset.exists()

    @classmethod
    def create_script(
        cls,
        command_name,
        execution_type="ONETIME",
        execution_status="PENDING",
        datetime=None,
        execution_log="",
        created_by=None,
        updated_by=None,
    ):
        """
        Create a new ExecuteScript entry with sensible defaults.

        Args:
            command_name (str): Name of the command to execute
            execution_type (str, optional): Either 'ONETIME' or 'EVERYTIME'. Defaults to 'ONETIME'.
            execution_status (str, optional): Status of execution. Defaults to 'PENDING'.
            datetime (datetime, optional): Date and time for script execution. Defaults to now.
            execution_log (str, optional): Rich text log of execution. Defaults to empty string.
            created_by (User, optional): User who created the script. Defaults to first superuser.
            updated_by (User, optional): User who updated the script. Defaults to first superuser.

        Returns:
            ExecuteScript: The created script instance

        Raises:
            ValueError: If execution_type is not valid
        """
        valid_types = [choice[0] for choice in cls.EXECUTION_TYPE_CHOICES]
        if execution_type not in valid_types:
            raise ValueError(
                f"execution_type must be one of {valid_types}, got '{execution_type}'"
            )

        valid_statuses = [choice[0] for choice in cls.EXECUTION_STATUS_CHOICES]
        if execution_status not in valid_statuses:
            raise ValueError(
                f"execution_status must be one of {valid_statuses}, got '{execution_status}'"
            )

        if datetime is None:
            datetime = timezone.now()

        if created_by is None or updated_by is None:
            default_user = get_user_model().objects.filter(is_superuser=True).first()
            if created_by is None:
                created_by = default_user
            if updated_by is None:
                updated_by = default_user

        return cls.objects.create(
            command_name=command_name,
            execution_type=execution_type,
            execution_status=execution_status,
            datetime=datetime,
            execution_log=execution_log,
            created_by=created_by,
            updated_by=updated_by,
        )


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
