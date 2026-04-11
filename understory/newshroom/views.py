from django.shortcuts import render,get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import (SearchVector,SearchQuery,SearchRank)
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from taggit.models import Tag
from .models import Article
from .forms import NewsLetterForm, RequestForm,SearchForm
from mycelium.utils import create_action


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
    
    # Form for submitting new article requests
    form = RequestForm()
    
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
        {'articles': articles, 'form': form, 'tag': tag, 'spotted_ids': spotted_ids}
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
            'user_has_spotted': user_has_spotted,
        }
    )

def news_letter(request, article_id):
    """Display newsletter form to share an article via email.
    
    Allows users to recommend articles to others via email.
    """
    # Get the article to be shared
    article = get_object_or_404(
        Article,
        id = article_id,
        status = Article.Status.PUBLISHED
    )
    sent = False
    if request.method == 'POST':
        form = NewsLetterForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            article_url = request.build_absolute_uri(
                article.get_absolute_url()
            )
            # Compose personalized email
            subject = (
                f'{cd['name']} recommends {article.title}'
            )
            message=(
                f'{article.title}\n{article.body}'
            )
            send_mail(
                subject = subject,
                message = message,
                from_email=None,
                recipient_list=[cd['email']]
            )
            sent = True
    else:
        form = NewsLetterForm()
    return render(
        request,
        'newshroom/newsletter.html',
        {
            'form':form,
            'sent':sent,
            'article':article,
        }
    )
@require_POST
def shroom_request(request):
    """Accept and save article request/suggestion from user.
    
    Only accepts POST requests.
    """
    form = RequestForm(data=request.POST)
    if form.is_valid():
        # Save the request to database
        shroom_request = form.save(commit=False)
        shroom_request.save()
        messages.success(request, "Thanks! Your request has been received.")
        return redirect('newshroom:article_list')
    # If form is invalid, re-render article list with error messages
    articles = Article.published.all()
    return render(
        request,
        'newshroom/article/list.html',
        {
            'form': form,
            'articles': articles,
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
            'results':results
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