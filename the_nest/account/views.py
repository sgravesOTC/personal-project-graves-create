from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Profile, Child
from .forms import AddChildForm, UserRegistrationForm, OnboardingForm, CHILD_FORMSET_FIELDS
from .utils import create_action
from django.forms import modelformset_factory

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            create_action(new_user, 'created an account')
            return render(
                request,
                'account/register_done.html',
                {'new_user':new_user, 'section': 'account'}
            )
    else:
        user_form = UserRegistrationForm()
        return render(
            request,
            'account/register.html',
            {'user_form':user_form, 'section': 'account'}
        )
    
def onboarding(request):
    
    ChildFormSet = modelformset_factory(
        Child,
        fields = CHILD_FORMSET_FIELDS,
    )

    if request.method == 'POST':
        onboarding_form = OnboardingForm(request.POST)
        child_formset = ChildFormSet(request.POST)

        if onboarding_form.is_valid() and child_formset.is_valid():
            profile = onboarding_form.save(commit=False)
            profile.user = request.user
            profile.save()
            
            children = child_formset.save(commit=False)
            for child in children:
                child.parent = profile
                child.save()
        
        else:
            onboarding_form = OnboardingForm()
            child_formset = ChildFormSet()

        return render(request, 'account/edit_profile.html',{
            'form':onboarding_form,
            'child_formset':child_formset,
            'section':'account'
        })