from django import forms
from django.contrib.auth import get_user_model

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelFomr)
    password = forms.CharField(
        label = 'Password',
        widget = forms.PasswordInput
    )
    password2 = forms.charfield(
        label = 'Repeat Password',
        widget = forms.PasswordInput
    )
    class Meta:
        model = get_user_model()
        fields = ['username','first_name','last_name','email']
    def clean_password2(self):
        cd = self.clean_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']
