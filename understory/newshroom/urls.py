from django.urls import path
from . import views

app_name = 'newshroom'

urlpatterns = [
    path('',views.article_list, name='article_list'),
    path('<int:id>/', views.post_detail, name = 'post_detail'),
]