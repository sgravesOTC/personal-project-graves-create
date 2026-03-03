from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

app_name = 'fairyring'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', views.dashboard, name='dashboard'),
    path('register/',views.register,name='register')
]