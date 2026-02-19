from collections import defaultdict
from datetime import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from enquiries.models import GeneralEnquiry, ProductEnquiry
from products.models import Product


def _staff_check(user):
    return user.is_staff


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(_staff_check), name='dispatch')
class BusinessDashboardView(TemplateView):
    template_name = 'dashboard/business_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_products = Product.objects.count()
        total_general_enquiries = GeneralEnquiry.objects.count()
        total_product_enquiries = ProductEnquiry.objects.count()
        total_enquiries = total_general_enquiries + total_product_enquiries

        recent_general = list(
            GeneralEnquiry.objects.values('name', 'email', 'resolved', 'created_at')
            .order_by('-created_at')[:5]
        )
        for item in recent_general:
            item['enquiry_type'] = 'General'
            item['product_name'] = '-'

        recent_product = list(
            ProductEnquiry.objects.values('name', 'email', 'resolved', 'created_at', 'product__name')
            .order_by('-created_at')[:5]
        )
        for item in recent_product:
            item['enquiry_type'] = 'Product'
            item['product_name'] = item.pop('product__name')

        recent_enquiries = sorted(
            recent_general + recent_product,
            key=lambda entry: entry['created_at'],
            reverse=True,
        )[:5]

        enquiries_per_product = list(
            ProductEnquiry.objects.values('product__name')
            .annotate(total=Count('id'))
            .order_by('-total', 'product__name')
        )

        month_totals = defaultdict(int)

        general_by_month = (
            GeneralEnquiry.objects.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
        )
        for row in general_by_month:
            if row['month']:
                month_totals[row['month']] += row['total']

        product_by_month = (
            ProductEnquiry.objects.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
        )
        for row in product_by_month:
            if row['month']:
                month_totals[row['month']] += row['total']

        enquiries_per_month = [
            {'month': datetime(month.year, month.month, 1), 'total': total}
            for month, total in sorted(month_totals.items())
        ]

        context.update(
            {
                'total_products': total_products,
                'total_enquiries': total_enquiries,
                'total_general_enquiries': total_general_enquiries,
                'total_product_enquiries': total_product_enquiries,
                'recent_enquiries': recent_enquiries,
                'enquiries_per_product': enquiries_per_product,
                'enquiries_per_month': enquiries_per_month,
            }
        )
        return context
