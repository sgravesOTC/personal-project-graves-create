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

@login_required
def onboarding(request):
    profile = request.user.profile
    ChildFormSet = modelformset_factory(
        Child,
        fields=CHILD_FORMSET_FIELDS,
        extra=1,
    )

    if request.method == 'POST':
        onboarding_form = OnboardingForm(request.POST, instance=profile)
        child_formset = ChildFormSet(request.POST, queryset=Child.objects.none())

        if onboarding_form.is_valid() and child_formset.is_valid():
            profile = onboarding_form.save(commit=False)
            profile.onboarding_complete = True
            profile.save()

            children = child_formset.save(commit=False)
            for child in children:
                child.parent = profile
                child.save()

            return redirect('dashboard')
    else:
        onboarding_form = OnboardingForm(instance=profile)
        child_formset = ChildFormSet(queryset=Child.objects.none())

    return render(request, 'account/onboarding.html', {
        'form': onboarding_form,
        'child_formset': child_formset,
        'section': 'account'
    })
    
@login_required
def add_child(request):
    if request.method == 'POST':
        form = AddChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user.profile
            child.save()
            create_action(request.user, 'added a child')
            return redirect('dashboard')
    else:
        form = AddChildForm()
    return render(request, 'account/add_child.html', {'form': form})

