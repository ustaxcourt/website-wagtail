from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def send_digest_email():
    """
    Calls the send_moderator_digest management command.
    """
    try:
        logger.info("Starting the send_moderator_digest job...")
        call_command('send_moderator_digest')
        logger.info("Successfully finished the send_moderator_digest job.")
    except Exception as e:
        logger.error(f"Error running send_moderator_digest job: {e}")