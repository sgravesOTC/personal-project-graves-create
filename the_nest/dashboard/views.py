from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def index(request):
    return render(request, 'dashboard/index.html')

@login_required
def dashboard(request):
    profile = request.user.profile
    children = profile.child.all()
    return render(request, 'dashboard/dashboard.html', {'profile': profile, 'children': children})
