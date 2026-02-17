from django import forms
from django.conf import settings
from .models import GeneralEnquiry, ProductEnquiry
from .recaptcha import verify_recaptcha


class BaseStyledFormMixin:
    def _apply_bootstrap_classes(self):
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.SelectMultiple):
                css = 'w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-800 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-300/40'
            else:
                css = 'w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2.5 text-slate-800 focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-300/40'
            if isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs.pop('class', None)
            else:
                field.widget.attrs['class'] = css
                if name != 'products':
                    field.widget.attrs.setdefault('placeholder', ' ')


class BaseEnquiryValidationMixin:
    def _client_ip(self):
        request = self.initial.get('request_obj')
        if not request:
            return None

        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError('Message should be at least 10 characters long.')
        return message

    def clean(self):
        cleaned_data = super().clean()
        if settings.RECAPTCHA_ENABLED:
            token = cleaned_data.get('recaptcha_token', '')
            if not verify_recaptcha(token, self._client_ip()):
                self.add_error('recaptcha_token', 'reCAPTCHA verification failed. Please try again.')
        return cleaned_data


class GeneralEnquiryForm(BaseStyledFormMixin, BaseEnquiryValidationMixin, forms.ModelForm):
    recaptcha_token = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = GeneralEnquiry
        fields = ['products', 'name', 'email', 'phone', 'message']
        widgets = {
            'products': forms.SelectMultiple(attrs={'size': 6}),
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['email'].label = 'Email (Optional)'
        self._apply_bootstrap_classes()


class ProductEnquiryForm(BaseStyledFormMixin, BaseEnquiryValidationMixin, forms.ModelForm):
    recaptcha_token = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ProductEnquiry
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['email'].label = 'Email (Optional)'
        self._apply_bootstrap_classes()
