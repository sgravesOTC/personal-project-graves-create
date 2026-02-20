from django.shortcuts import render,get_object_or_404
from .models import Article

# Create your views here.
def article_list(request):
    articles = Article.publisher.all()
    return render(
        request,
        'blog/article/list.html',
        {'articles':articles}
    )

def article_detail(request):
    article = get_object_or_404(
        Article,
        id = id,
        status = Article.Status.PUBLISHED
    )
    return render(
        request,
        'blog/article/detail.html'
    )