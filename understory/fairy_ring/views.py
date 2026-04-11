from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, ForagerConnection
from sporeprint.models import Specimen
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

# Create your views here.
User = get_user_model()

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

@login_required
@require_POST
def forager_follow(request):
    forager_id = request.POST.get('id')
    action = request.POST.get('action')
    username = request.POST.get('username')

    if forager_id and action and username:
        target_user = get_object_or_404(User, id=forager_id)

        if target_user == request.user:
            messages.error(request, "You can't follow yourself.")
        elif action == 'follow':
            ForagerConnection.objects.get_or_create(
                forager_from=request.user,
                forager_to=target_user
            )
        elif action == 'unfollow':
            ForagerConnection.objects.filter(
                forager_from=request.user,
                forager_to=target_user
            ).delete()

        return redirect('fairy_ring:forager_detail', username=username)

    return redirect('fairy_ring:forager_list')

@login_required
def forager_list(request):
    foragers = Profile.objects.select_related('user')

    return render(request, 'fairy_ring/forager_list.html', {
        'foragers': foragers,
        'section': 'foragers'
    })

@login_required
def forager_detail(request, username):
    profile_user = get_object_or_404(User, username=username)

    profile = get_object_or_404(Profile, user=profile_user)

    is_following = (
        request.user.is_authenticated and ForagerConnection.objects.filter(
            forager_from=request.user,
            forager_to=profile_user
        ).exists()
    )

    specimens = profile_user.sporeprint_collected.all()[:12]

    return render(request, 'fairy_ring/forager_detail.html', {
        'profile_user': profile_user,
        'profile': profile,
        'is_following': is_following,
        'specimens': specimens,
        'section': 'foragers'
    })