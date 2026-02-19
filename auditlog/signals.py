import logging

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import Signal, receiver

from enquiries.models import GeneralEnquiry, ProductEnquiry
from products.models import Product

from .context import get_current_ip, get_current_user
from .models import AuditLog

logger = logging.getLogger('django')

dashboard_accessed = Signal()


def _create_audit_log(action, model_name, object_id=''):
    try:
        AuditLog.objects.create(
            user=get_current_user(),
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id is not None else '',
            ip_address=get_current_ip(),
        )
    except Exception:
        logger.exception('Failed to write audit log for %s (%s)', action, model_name)


@receiver(user_logged_in)
def log_admin_login(sender, request, user, **kwargs):
    admin_url = '/' + settings.ADMIN_URL.lstrip('/')
    admin_login_url = '/' + settings.ADMIN_LOGIN_URL.lstrip('/')
    request_path = request.path

    if request_path.startswith(admin_url) or request_path.startswith(admin_login_url) or request_path == '/admin/login/':
        _create_audit_log('ADMIN_LOGIN', 'User', user.pk)


@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    action = 'PRODUCT_CREATED' if created else 'PRODUCT_UPDATED'
    _create_audit_log(action, 'Product', instance.pk)


@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    _create_audit_log('PRODUCT_DELETED', 'Product', instance.pk)


@receiver(pre_save, sender=GeneralEnquiry)
def capture_general_enquiry_previous(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_resolved = None
    else:
        previous = sender.objects.filter(pk=instance.pk).values_list('resolved', flat=True).first()
        instance._previous_resolved = previous


@receiver(post_save, sender=GeneralEnquiry)
def log_general_enquiry_status_change(sender, instance, created, **kwargs):
    if created:
        return
    previous = getattr(instance, '_previous_resolved', None)
    if previous is not None and previous != instance.resolved:
        _create_audit_log('GENERAL_ENQUIRY_STATUS_CHANGED', 'GeneralEnquiry', instance.pk)


@receiver(pre_save, sender=ProductEnquiry)
def capture_product_enquiry_previous(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_resolved = None
    else:
        previous = sender.objects.filter(pk=instance.pk).values_list('resolved', flat=True).first()
        instance._previous_resolved = previous


@receiver(post_save, sender=ProductEnquiry)
def log_product_enquiry_status_change(sender, instance, created, **kwargs):
    if created:
        return
    previous = getattr(instance, '_previous_resolved', None)
    if previous is not None and previous != instance.resolved:
        _create_audit_log('PRODUCT_ENQUIRY_STATUS_CHANGED', 'ProductEnquiry', instance.pk)


@receiver(dashboard_accessed)
def log_dashboard_access(sender, request, **kwargs):
    user = getattr(request, 'user', None)
    if user and user.is_authenticated and user.is_staff:
        _create_audit_log('DASHBOARD_ACCESS', 'BusinessDashboard', '')
