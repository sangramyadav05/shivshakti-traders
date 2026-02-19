from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password

from .models import DashboardUser


class DashboardUserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text='Set a strong password for dashboard login.',
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = DashboardUser
        fields = ('username', 'is_active')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            self.add_error('password2', 'Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.password = make_password(self.cleaned_data['password1'])
        if commit:
            obj.save()
        return obj


class DashboardUserChangeForm(forms.ModelForm):
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput,
        required=False,
        help_text='Leave blank if you do not want to change password.',
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = DashboardUser
        fields = ('username', 'is_active')

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')

        if p1 or p2:
            if p1 != p2:
                self.add_error('new_password2', 'New passwords do not match.')
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password1')
        if new_password:
            obj.password = make_password(new_password)
        if commit:
            obj.save()
        return obj


@admin.register(DashboardUser)
class DashboardUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('username',)
    ordering = ('username',)
    readonly_fields = ('created_at',)

    add_form = DashboardUserCreateForm
    form = DashboardUserChangeForm

    fieldsets = (
        ('Dashboard User', {'fields': ('username', 'is_active')}),
        ('Change Password', {'fields': ('new_password1', 'new_password2')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    add_fieldsets = (
        ('Dashboard User', {'fields': ('username', 'is_active')}),
        ('Set Password', {'fields': ('password1', 'password2')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
            defaults['fields'] = ('username', 'is_active', 'password1', 'password2')
        kwargs.update(defaults)
        return super().get_form(request, obj, **kwargs)

