from django.shortcuts import render,get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import (SearchVector,SearchQuery,SearchRank)
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib import messages
from django.core.mail import send_mail
from taggit.models import Tag
from .models import Article
from .forms import NewsLetterForm, RequestForm,SearchForm


# Create your views here.
def article_list(request, tag_slug = None):
    article_list = Article.publisher.all()
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
    return render(
        request,
        'newshroom/article/list.html',
        {'articles':articles,'form':form, 'tag':tag}
    )

def article_detail(request, year, month, article):
    article = get_object_or_404(
        Article,
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

    return render(
        request,
        'newshroom/article/detail.html',
        {
            'article':article,
            'similar_articles':similar_articles
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
                Article.publisher.annotate(
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