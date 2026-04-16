from django.shortcuts import render
from newshroom.models import Article
from sporeprint.models import Specimen
from fieldnotes.models import ForagingReport


def index(request):
    """
    Home page view displaying:
    - Most liked articles
    - Most liked specimens
    - Most recent foraging reports
    """
    # Get top 4 most liked articles
    top_articles = Article.publisher.all().order_by('-total_spots')[:4]
    
    # Get top 4 most liked specimens
    top_specimens = Specimen.objects.all().order_by('-total_spots')[:4]
    
    # Get 4 most recent foraging reports
    recent_reports = ForagingReport.objects.all().order_by('-created')[:4]
    
    context = {
        'section': 'home',
        'top_articles': top_articles,
        'top_specimens': top_specimens,
        'recent_reports': recent_reports,
    }
    
    return render(request, 'home/index.html', context)
