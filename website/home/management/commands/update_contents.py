from django.core.management.base import BaseCommand
from django.db import transaction

from home.models.utils.update_scripts import PostDeploymentScript


# List of update script classes to execute
update_scripts_to_run = [
    # Add your update script classes here
    # Example: SomeUpdateScript,
]


class Command(BaseCommand):
    help = "Execute update content scripts that haven't been run yet, tracking execution in PostDeploymentScript model."

    def handle(self, *args, **options):  # noqa: ARG002
        executed_count = 0
        skipped_count = 0

        for script_class in update_scripts_to_run:
            script_name = script_class.__name__

            # Check if this script has already been executed
            if PostDeploymentScript.objects.filter(script_name=script_name).exists():
                self.stdout.write(
                    self.style.WARNING(f"Skipping {script_name} - already executed")
                )
                skipped_count += 1
                continue

            try:
                with transaction.atomic():
                    # Execute the script
                    script_instance = script_class()
                    script_instance.run()

                    # Record the execution
                    PostDeploymentScript.objects.create(script_name=script_name)

                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully executed {script_name}")
                    )
                    executed_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to execute {script_name}: {str(e)}")
                )
                # Don't record failed executions so they can be retried
                continue

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"Update contents command completed. "
                f"Executed: {executed_count}, Skipped: {skipped_count}"
            )
        )
