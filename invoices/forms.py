from django import forms


class GenerateInvoiceForm(forms.Form):
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month'}),
        input_formats=['%Y-%m', '%Y-%m-%d']
    )


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
