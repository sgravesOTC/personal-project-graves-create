from django.urls import path
from . import views

app_name = 'fairy_ring'

urlpatterns = [
    path('login/', views.user_login, name='login'),
]
