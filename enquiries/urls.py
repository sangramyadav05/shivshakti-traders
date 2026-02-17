from django.urls import path
from .views import EnquirySuccessView, GeneralEnquiryCreateView, ProductEnquiryCreateView

app_name = 'enquiries'

urlpatterns = [
    path('enquiry/', GeneralEnquiryCreateView.as_view(), name='enquiry'),
    path('product/<slug:slug>/', ProductEnquiryCreateView.as_view(), name='product_enquiry'),
    path('success/', EnquirySuccessView.as_view(), name='enquiry_success'),
]
