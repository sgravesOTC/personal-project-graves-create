from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .forms import LoginForm, UserRegistrationForm

def user_login(request):
    if request.method == 'POST':
        # Bind the submitted POST data to the form
        form = LoginForm(request.POST)
        if form.is_valid():
            # cleaned_data contains the sanitized, validate values
            cd = form.cleaned_data

            # authenticate() checks credenttials against the database
            # Returns a User object if valid, or None if not
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )
            if user is not None:
                if user.is_active:
                    # login() writes the verified user into the current session
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    # User exists but has been deactivated in the admin
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        # GET request - Just show the empty form
        form = LoginForm()
    return render(request, 'fairyring/login.html', {'form':form})

@login_required
def dashboard(request):
    return render(
        request,
        'fairyring/dashboard.html',
        # section variable used to highlight the correct nav item
        {'section':'undergrowth'}
    )

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)

            new_user.set_password(
                user_form.cleaned_data['password']
            )

            new_user.save()

            return render(
                request,
                'fairyring/register_done.html',
                {'new_user': new_user}
            )
        else:
            user_form = UserRegistrationForm()
            return render(
                request,
                'fairyring/register.html',
                {'user_form': user_form}
                )
    else:
        user_form = UserRegistrationForm()
    return render(
        request,
        'fairyring/register.html',
        {'user_form':user_form}   
    )