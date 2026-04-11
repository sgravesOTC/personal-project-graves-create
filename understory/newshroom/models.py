from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from taggit.managers import TaggableManager

# ================== NEWSHROOM APP ==================
# This app manages blog articles about mushrooms and fungal information.
# Users will be able to create, read, and recommend articles.
# Articles can be tagged, spotted (liked), and shared via newsletter.


class Publisher(models.Manager):
    """Custom manager that returns only published articles."""
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=Article.Status.PUBLISHED)
        )


class Article(models.Model):
    """Informational articles about mushroom species and fungal topics.
    
    Attributes:
        image: Featured image for the article
        title: Article headline
        slug: URL-friendly identifier (unique per publish date)
        author: Foreign key to User who wrote the article
        body: Full article text (supports markdown)
        publish: Publication date/time
        status: Draft or Published state
        spotted_by: Users who have marked this article as useful
        total_spots: Cached count of users who spotted this article
        tags: Flexible tagging system using django-taggit
    """
    
    class Status(models.TextChoices):
        DRAFT = 'DF','Draft'
        PUBLISHED = 'PB','Published'

    image = models.ImageField()
    title = models.CharField(max_length=250)
    slug = models.CharField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='newshroom_articles'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    spotted_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='newshroom_spotted',
        blank=True,
    )
    total_spots = models.PositiveIntegerField(default=0)

    tags = TaggableManager()

    # Two managers: 'objects' for all articles, 'publisher' for published only
    objects = models.Manager()
    publisher = Publisher()
    
    class Meta:
        ordering = ['-publish']  # Newest articles first
        indexes = [
            models.Index(fields=['-publish']),  # Speed up sorting by most recent
        ]

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse(
            'newshroom:article_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.slug
            ]
        )

class Request(models.Model):
    """User-submitted article requests and suggestions.
    
    Allows readers to suggest new topics they'd like to see covered.
    
    Attributes:
        name: Submitter's name
        email: Contact email
        body: The request/suggestion text
        created: When the request was submitted
        updated: When the request was last modified
        active: Whether this request is still open
    """
    name = models.CharField(max_length=250)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering=['created']  # Oldest requests first
        indexes = [models.Index(fields=['created','name'])]  # Speed up filtering and sorting

    def __str__(self):
        return f'Request by {self.name}: {self.body}'