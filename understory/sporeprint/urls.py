from django.urls import path
from . import views

app_name = 'sporeprint'

urlpatterns = [
    path('create/', views.specimen_create, name='specimen_create'),
    path('<int:id>/<slug:slug>/', views.specimen_detail, name='specimen_detail'),
    path('<int:id>/<slug:slug>/edit/', views.specimen_edit, name='specimen_edit'),
    path('<int:id>/<slug:slug>/delete/', views.specimen_delete, name='specimen_delete'),
    path('like/', views.specimen_like, name='specimen_like'),
    path('collection/', views.specimen_list, name='specimen_list'),
]