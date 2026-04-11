from django.urls import path
from . import views

# URL namespace for the Newshroom article app
app_name = 'newshroom'

# ================== ARTICLE URL PATTERNS ==================
# All articles are publicly viewable but require authentication to interact

urlpatterns = [
    # Articles homepage - paginated list of all published articles
    path('', views.article_list, name='article_list'),
    
    # Article detail page - uses year/month/slug for archive-friendly URLs
    # Example: /articles/2026/4/mushroom-identification/
    path('<int:year>/<int:month>/<slug:article>/', views.article_detail, name='article_detail'),
    
    # Newsletter sharing page - recommend article to others via email
    path('<int:article_id>/newsletter/', views.news_letter, name='news_letter'),
    
    # Form endpoint for submitting article requests/suggestions
    path('request/', views.shroom_request, name='shroom_request'),
    
    # Filtered list - show only articles with a specific tag
    # Example: /articles/tag/edible/
    path('tag/<slug:tag_slug>/', views.article_list, name='article_list_by_tag'),
    
    # Full-text search across article titles and body content
    path('search/', views.article_search, name='article_search'),
    
    # AJAX endpoint - spot/unspot articles (requires login)
    path('like/', views.article_like, name='article_like'),
]