from django.apps import AppConfig
import os

class ScheduledJobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.scheduled_jobs'
    verbose_name = "Scheduled Jobs"

    def ready(self):
        # The 'run_main' check prevents the scheduler from running twice in development
        # when Django's reloader is active.
        if os.environ.get('RUN_MAIN', None) != 'true':
            from . import jobs # Import your jobs module
            from apscheduler.schedulers.background import BackgroundScheduler

            scheduler = BackgroundScheduler()
            # scheduler.add_job(
            #     jobs.send_digest_email,
            #     trigger='cron',
            #     hour='10',  # Runs at 10:00 AM
            #     minute='00', #
            #     id='send_digest_email_job', # A unique ID for the job
            #     max_instances=1,
            #     replace_existing=True, # Overwrites a job with the same ID
            # )
            scheduler.add_job(
                jobs.send_digest_email,
                trigger='interval',         # Change trigger to 'interval'
                minutes=2,                  # Set the interval
                id='send_digest_email_job',
                max_instances=1,
                replace_existing=True,
            )


            try:
                scheduler.start()
                print("Scheduler started...")
            except Exception as e:
                print(f"Error starting scheduler: {e}")
                # In case of errors, like the database not being ready, you might want to handle this.