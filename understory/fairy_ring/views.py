from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from sporeprint.models import Specimen

# Create your views here.

@login_required
def fairy_ring(request):
    specimens = Specimen.objects.filter(collector=request.user)
    return render(
        request,
        'fairy_ring/fairy_ring.html',
        {'section': 'fairy_ring', 'specimens': specimens}
    )

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(
                request,
                'fairy_ring/register_done.html',
                {'new_user':new_user}
            )
    else:
        user_form = UserRegistrationForm()
        return render(
            request,
            'fairy_ring/register.html',
            {'user_form':user_form}
        )
    
@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance = request.user,
            data = request.POST
        )
        profile_form = ProfileEditForm(
            instance = request.user.profile,
            data = request.POST,
            files = request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request,
                'Profile updated successfully!'
            )
        else:
            messages.error(request, 'There was an error updating your profile.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance = request.user.profile)
    return render(
        request,
        'fairy_ring/edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form
        }
    )