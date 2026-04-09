from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def hollow(request):
    return render(
        request,
        'fairy_ring/hollow.html',
        {'section':'hollow'}
    )