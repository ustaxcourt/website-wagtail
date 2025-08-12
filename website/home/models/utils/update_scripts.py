from django.db import models


class PostDeploymentScript(models.Model):
    script_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Filename of the script that was executed.",
    )
    executed_at = models.DateTimeField(
        auto_now_add=True, help_text="Script executed time."
    )

    def __str__(self):
        return (
            f"{self.script_name} run on {self.executed_at.strftime('%Y-%m-%d %H:%M')}"
        )
