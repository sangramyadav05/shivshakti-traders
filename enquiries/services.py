import logging

from .models import GeneralEnquiry, ProductEnquiry
from .tasks import send_enquiry_email_task

logger = logging.getLogger('enquiries')


def queue_enquiry_notification(enquiry):
    if isinstance(enquiry, ProductEnquiry):
        enquiry_type = 'product'
    elif isinstance(enquiry, GeneralEnquiry):
        enquiry_type = 'general'
    else:
        logger.warning('Unsupported enquiry instance for email queue: %s', type(enquiry).__name__)
        return

    try:
        send_enquiry_email_task.delay(enquiry_type, enquiry.id)
        logger.info('Queued %s enquiry email notifications for id=%s', enquiry_type, enquiry.id)
    except Exception:
        logger.exception('Failed to queue %s enquiry email notifications for id=%s', enquiry_type, enquiry.id)
