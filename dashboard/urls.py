from django.urls import path

from .views import BusinessDashboardView

app_name = 'dashboard'

urlpatterns = [
    path('', BusinessDashboardView.as_view(), name='business_dashboard'),
]
