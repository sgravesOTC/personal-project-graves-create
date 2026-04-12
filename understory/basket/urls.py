from django.urls import path
from . import views

app_name = 'basket'

urlpatterns = [
    path('',views.basket_detail, name='basket_detail'),
    path('add/<int:species_id>/', views.basket_add, name = 'basket_add'),
    path('remove/<int:species_id>/', views.basket_remove, name = 'basket_remove')
]
