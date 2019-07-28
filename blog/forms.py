from django import forms
from .models import EmailPush


class EmailForm(forms.ModelForm):
    """Eメール通知の登録用フォーム"""

    class Meta:
        model = EmailPush
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        EmailPush.objects.filter(email=email, is_active=False).delete()
        return email
