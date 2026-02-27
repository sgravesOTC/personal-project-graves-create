from django import template
from ..models import Article
import markdown
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def total_articles():
    return Article.publisher.count()

@register.inclusion_tag('newshroom/article/latest_article.html')
def show_latest(count=5):
    latest_articles = Article.publisher.order_by('-publish')[:count]
    return {'latest_articles':latest_articles}

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))