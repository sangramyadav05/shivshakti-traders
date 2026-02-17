from django.urls import path
from .views import AccountDashboardView, AccountLoginView, AccountLogoutView, StaffAdminLoginView

app_name = 'accounts'

urlpatterns = [
    path('login/', AccountLoginView.as_view(), name='login'),
    path('logout/', AccountLogoutView.as_view(), name='logout'),
    path('dashboard/', AccountDashboardView.as_view(), name='dashboard'),
    path('admin-login/', StaffAdminLoginView.as_view(), name='admin_login'),
]
