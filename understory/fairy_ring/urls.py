from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'fairy_ring'

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='fairy_ring/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='fairy_ring/logout.html'), name='logout'),
    path('',views.hollow, name='hollow'),
]
