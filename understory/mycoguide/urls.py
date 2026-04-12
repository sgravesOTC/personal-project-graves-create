from django.urls import path
from . import views

app_name = 'mycoguide'

urlpatterns = [
    path('', views.species_list, name='species_list'),
    path(
        '<slug:genus_slug>/',
        views.species_list,
        name='species_list_by_genus'
    ),
    path(
        '<int:id>/<slug:slug>/',
        views.species_detail,
        name='species_detail'
    ),
]
