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

class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(
            id = self.instance.id
        ).filter(
            email=data
        )
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'pronouns_1', 'pronouns_2']  # TODO: Add privacy_level and timezone
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'pronouns_1': forms.Select(attrs={'class': 'form-select'}),
            'pronouns_2': forms.Select(attrs={'class': 'form-select'}),
        }