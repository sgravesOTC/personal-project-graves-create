from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import (SearchVector,SearchQuery,SearchRank)
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from taggit.models import Tag
from .models import Article
from .forms import SearchForm
from mycelium.utils import create_action
from .recommender import ArticleRecommender


# ================== NEWSHROOM VIEWS ==================
# Views for displaying, searching, and interacting with mushroom articles.


def article_list(request, tag_slug = None):
    """Display paginated list of published articles, optionally filtered by tag.
    
    - Uses select_related('author') and prefetch_related('tags') for efficiency
    - Paginates 3 articles per page
    - Tracks which articles current user has spotted
    - Optionally filters by a specific tag
    """
    # Fetch published articles with author and tags pre-loaded
    article_list = Article.publisher.select_related('author').prefetch_related('tags').all()
    tag = None
    if tag_slug:
        # If a tag is specified, filter articles by that tag
        tag = get_object_or_404(Tag, slug=tag_slug)
        article_list = article_list.filter(tags__in=[tag])
    
    # Paginate results (3 articles per page)
    paginator = Paginator(article_list, 3)
    page_number = request.GET.get('page',1)
    
    # Handle pagination edge cases
    try:
        articles = paginator.page(page_number)
    except EmptyPage:
        # If page is too high, show last page
        articles = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # If page is invalid, show first page
        articles = paginator.page(1)
    
    # Get IDs of articles this user has spotted, for client-side UI updates
    spotted_ids = (
        set(request.user.newshroom_spotted.values_list('id', flat=True))
        if request.user.is_authenticated else set()
    )
    return render(
        request,
        'newshroom/article/list.html',
        {'articles': articles, 'tag': tag, 'spotted_ids': spotted_ids, 'section': 'newshroom'}
    )


def article_detail(request, year, month, article):
    """Display a single article with similar articles recommended.
    
    Uses year/month/slug URL structure for human-readable URLs and archives.
    Finds similar articles by matching tags and sorting by relevance.
    """
    # Fetch the article by URL parameters and publication status
    article = get_object_or_404(
        Article.objects.select_related('author'),
        status = Article.Status.PUBLISHED,
        slug = article,
        publish__year=year,
        publish__month=month
    )
    # Track article in session history
    history = request.session.get('article_history', [])
    if article.id not in history:
        history.append(article.id)
        request.session['article_history']=history

    # Record co-occurance with previously read articles
    try:
        r = ArticleRecommender()
        if len(history) > 1:
            previously_read = Article.publisher.filter(id__in = history).exclude(id=article.id)
            r.articles_read([article]+list(previously_read))
        recommended_articles = r.suggest_articles_for(article)
    except Exception:
        recommended_articles = []

    # Find similar articles by shared tags
    article_tags_ids = article.tags.values_list('id', flat=True)
    # Filter to other published articles with any of the same tags
    similar_articles = Article.publisher.filter(
        tags__in = article_tags_ids
    ).exclude(id=article.id)  # Exclude the current article
    
    # Rank by number of matching tags, then by recency
    similar_articles = similar_articles.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags','-publish')[:4]  # Limit to 4 similar articles

    # Check if current user has already spotted this article
    user_has_spotted = (
        request.user.is_authenticated and article.spotted_by.filter(id=request.user.id).exists()
    )
    return render(
        request,
        'newshroom/article/detail.html',
        {
            'article': article,
            'similar_articles': similar_articles,
            'recommended_articles': recommended_articles,
            'user_has_spotted': user_has_spotted,
            'section': 'newshroom',
        }
    )

def article_search(request):
    """Full-text search across article titles and bodies.
    
    Uses PostgreSQL full-text search for relevance ranking.
    Results are ranked by match quality.
    """
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # Set up full-text search across title and body
            search_vector = SearchVector('title','body')
            search_query = SearchQuery(query)
            # Query and rank results by relevance
            results = (
                Article.publisher.select_related('author').annotate(
                    search = search_vector,
                    rank = SearchRank(search_vector,search_query)
                )
            ).filter(search=search_query).order_by('-rank')  # Most relevant first
    return render(
        request,
        'newshroom/search.html',
        {
            'form':form,
            'query':query,
            'results':results,
            'section': 'newshroom',
        }
    )


@login_required
@require_POST
def article_like(request):
    """Handle AJAX requests to spot/unspot articles.
    
    Requires: authenticated user and POST method.
    Returns: JSON with updated spot count.
    """
    article_id = request.POST.get('id')
    action = request.POST.get('action')  # 'spot' or 'unspot'

    if article_id and action:
        article = get_object_or_404(Article, id=article_id)

        if action == 'spot':
            # User is spotting the article
            article.spotted_by.add(request.user)
            article.total_spots += 1
            # Record this action for activity feed
            create_action(request.user, 'spotted', article)

        elif action == 'unspot':
            # User is removing their spot
            article.spotted_by.remove(request.user)
            article.total_spots -= 1

        article.save()
        return JsonResponse({'status': 'ok', 'total_spots': article.total_spots})

    # Invalid request parameters
    return JsonResponse({'status': 'error'}, status=400)