import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import GeneralEnquiry, ProductEnquiry

logger = logging.getLogger('enquiries')


def _admin_recipients():
    admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', '').strip()
    if admin_email:
        return [admin_email]
    return [email for _, email in getattr(settings, 'ADMINS', []) if email]


def _load_enquiry(enquiry_type, enquiry_id):
    if enquiry_type == 'product':
        return ProductEnquiry.objects.select_related('product').get(id=enquiry_id)
    if enquiry_type == 'general':
        return GeneralEnquiry.objects.prefetch_related('products').get(id=enquiry_id)
    raise ValueError(f'Unsupported enquiry type: {enquiry_type}')


def _build_context(enquiry_type, enquiry):
    if enquiry_type == 'product':
        product_name = enquiry.product.name
        enquiry_label = 'Product Enquiry'
        products_text = product_name
    else:
        products = list(enquiry.products.values_list('name', flat=True))
        product_name = '-'
        enquiry_label = 'General Enquiry'
        products_text = ', '.join(products) if products else 'No product selected'

    return {
        'enquiry_type': enquiry_type,
        'enquiry_label': enquiry_label,
        'enquiry': enquiry,
        'product_name': product_name,
        'products_text': products_text,
        'business_name': 'Shivshakti Traders',
        'support_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@shivshaktitraders.com'),
    }


def _send_html_email(subject, to_email, template_name, context):
    if not to_email:
        return False

    html_body = render_to_string(template_name, context)
    text_body = strip_tags(html_body)
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@shivshaktitraders.com'),
        to=[to_email],
    )
    message.attach_alternative(html_body, 'text/html')
    message.send(fail_silently=False)
    return True


@shared_task(name='enquiries.send_enquiry_email_task')
def send_enquiry_email_task(enquiry_type, enquiry_id):
    try:
        enquiry = _load_enquiry(enquiry_type, enquiry_id)
    except (GeneralEnquiry.DoesNotExist, ProductEnquiry.DoesNotExist):
        logger.warning('Enquiry not found for email task: type=%s id=%s', enquiry_type, enquiry_id)
        return {'status': 'not_found', 'enquiry_type': enquiry_type, 'enquiry_id': enquiry_id}
    except Exception:
        logger.exception('Failed loading enquiry for email task: type=%s id=%s', enquiry_type, enquiry_id)
        return {'status': 'load_error', 'enquiry_type': enquiry_type, 'enquiry_id': enquiry_id}

    context = _build_context(enquiry_type, enquiry)
    sent_admin = False
    sent_customer = False

    admin_recipients = _admin_recipients()
    for recipient in admin_recipients:
        try:
            sent_admin = _send_html_email(
                subject=f"New {context['enquiry_label']} Received",
                to_email=recipient,
                template_name='enquiries/emails/admin_enquiry_notification.html',
                context=context,
            ) or sent_admin
        except Exception:
            logger.exception('Failed sending admin enquiry email: type=%s id=%s recipient=%s', enquiry_type, enquiry_id, recipient)

    customer_email = (enquiry.email or '').strip()
    if customer_email:
        try:
            sent_customer = _send_html_email(
                subject=f"We received your enquiry - {context['business_name']}",
                to_email=customer_email,
                template_name='enquiries/emails/customer_enquiry_confirmation.html',
                context=context,
            )
        except Exception:
            logger.exception('Failed sending customer confirmation email: type=%s id=%s email=%s', enquiry_type, enquiry_id, customer_email)

    return {
        'status': 'completed',
        'enquiry_type': enquiry_type,
        'enquiry_id': enquiry_id,
        'admin_sent': sent_admin,
        'customer_sent': sent_customer,
    }
