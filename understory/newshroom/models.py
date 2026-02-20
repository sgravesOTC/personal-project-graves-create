from django.db import models
from django.utils import timezone
from django.conf import settings

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
    slug = models.CharField(max_length=250)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )

    objects = models.Manager()
    publisher = Publisher()
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title