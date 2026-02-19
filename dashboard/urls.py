from django.urls import path

from .views import (
    DashboardEnquiriesView,
    DashboardHomeView,
    DashboardLoginView,
    DashboardLogoutView,
    DashboardProductsView,
)

app_name = 'dashboard'

urlpatterns = [
    path('login/', DashboardLoginView.as_view(), name='dashboard_login'),
    path('logout/', DashboardLogoutView.as_view(), name='dashboard_logout'),
    path('home/', DashboardHomeView.as_view(), name='dashboard_home'),
    path('products/', DashboardProductsView.as_view(), name='dashboard_products'),
    path('enquiries/', DashboardEnquiriesView.as_view(), name='dashboard_enquiries'),
    path('', DashboardHomeView.as_view(), name='business_dashboard'),
]
