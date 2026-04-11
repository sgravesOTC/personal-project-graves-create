from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm

# Create your views here.

def fairy_ring(request):
    return render(
        request,
        'fairy_ring/fairy_ring.html',
        {'section':'fairy_ring'}
    )

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
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