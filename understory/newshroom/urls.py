from django.urls import path
from . import views


app_name = 'newshroom'

urlpatterns = [
    path('',views.article_list, name='article_list'),
    path('<int:year>/<int:month>/<slug:article>/', views.article_detail, name = 'article_detail'),
    path('<int:article_id>/newsletter/',views.news_letter,name='news_letter'),
    path('request/', views.shroom_request, name='shroom_request'),
    path('tag/<slug:tag_slug>/', views.article_list, name='article_list_by_tag'),
    path('search/', views.article_search, name='article_search'),
]