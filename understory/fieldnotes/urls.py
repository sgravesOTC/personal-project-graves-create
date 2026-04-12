from django.urls import path
from . import views

app_name = 'fieldnotes'

urlpatterns = [
    # List the logged-in user's foraging reports
    path('', views.report_list, name='report_list'),

    # Create a new foraging report
    path('create/', views.report_create, name='report_create'),

    # View a single report by its primary key
    path('<int:pk>/', views.report_detail, name='report_detail'),
]
