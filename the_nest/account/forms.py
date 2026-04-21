from django import forms
from django.contrib.auth import get_user_model
from .models import Profile, Child 
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    """
    User Registration Form for parents. 
    """
    password = forms.CharField(
        label = 'Password',
        widget = forms.PasswordInput
    )
    password2 = forms.CharField(
        label = 'Repeat Password',
        widget = forms.PasswordInput
    )
    class Meta:
        model = get_user_model()
        fields = ['username','first_name','last_name','email']
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']
    
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data
    
class OnboardingForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('bio','pronouns_1', 'pronouns_2',)

class AddChildForm(forms.ModelForm):

    class Meta:
        model = Child
        fields = ('first_name','pronouns_1','pronouns_2','age_range')

CHILD_FORMSET_FIELDS = ['first_name','pronouns_1','pronouns_2','age_range']