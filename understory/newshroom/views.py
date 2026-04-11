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


# Create your views here.
def article_list(request, tag_slug = None):
    article_list = Article.publisher.select_related('author').prefetch_related('tags').all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        article_list = article_list.filter(tags__in=[tag])
    form = RequestForm()
    paginator = Paginator(article_list, 3)
    page_number = request.GET.get('page',1)
    articles = paginator.page(page_number)
    try:
        articles = paginator.page(page_number)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        articles = paginator.page(1)
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
    article = get_object_or_404(
        Article.objects.select_related('author'),
        status = Article.Status.PUBLISHED,
        slug = article,
        publish__year=year,
        publish__month=month
    )

    article_tags_ids = article.tags.values_list('id', flat=True)
    similar_articles = Article.publisher.filter(
        tags__in = article_tags_ids
    ).exclude(id=article.id)
    similar_articles = similar_articles.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags','-publish')[:4]

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
    form = RequestForm(data=request.POST)
    if form.is_valid():
        shroom_request = form.save(commit=False)
        shroom_request.save()
        messages.success(request, "Thanks! Your request has been received.")
        return redirect('newshroom:article_list')
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
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title','body')
            search_query = SearchQuery(query)
            results = (
                Article.publisher.select_related('author').annotate(
                    search = search_vector,
                    rank = SearchRank(search_vector,search_query)
                )
            ).filter(search=search_query).order_by('-rank')
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
    article_id = request.POST.get('id')
    action = request.POST.get('action')

    if article_id and action:
        article = get_object_or_404(Article, id=article_id)

        if action == 'spot':
            article.spotted_by.add(request.user)
            article.total_spots += 1
            create_action(request.user, 'spotted', article)

        elif action == 'unspot':
            article.spotted_by.remove(request.user)
            article.total_spots -= 1

        article.save()
        return JsonResponse({'status': 'ok', 'total_spots': article.total_spots})

    return JsonResponse({'status': 'error'}, status=400)