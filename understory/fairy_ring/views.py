from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def fairy_ring(request):
    return render(
        request,
        'fairy_ring/fairy_ring.html',
        {'section':'fairy_ring'}
    )