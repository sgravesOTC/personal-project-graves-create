from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from taggit.managers import TaggableManager

# Create your models here.

class Publisher(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=Article.Status.PUBLISHED)
        )
# Informational Articles
class Article(models.Model):
    
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
    tags = TaggableManager()

    objects = models.Manager()
    publisher = Publisher()
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
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
    name = models.CharField(max_length=250)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering=['created']
        indexes = [models.Index(fields=['created','name'])]

    def __str__(self):
        return f'Request by {self.name}: {self.body}'