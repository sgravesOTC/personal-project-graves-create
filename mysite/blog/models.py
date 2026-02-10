from django.db import models
from django.utils import timezone
from django.conf import settings

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Article.Status.PUBLISHED)

# Article Model
class Article(models.Model):

    # Allows User to choose between published and draft
    class Status(models.TextChoices):
        DRAFT = 'DF','Draft'
        PUBLISHED = 'PB','Published'
    # Title, slug, and author
    title = models.CharField(max_length=250)
    slug = models.CharField(max_length=250)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_articles'
    )
    image = models.ImageField()
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    objects = models.Manager()
    published = PublishedManager()
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]
    def __str__(self):
        return self.title
    
class Reference(models.Model):
    author = models.CharField(max_length=50)
    publish= models.DateTimeField(default=None)
    title = models.CharField(max_length=250)
    ref_url = models.URLField(max_length=500, blank=True)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='references'
    )
    class Meta:
        ordering = ['-author']
        indexes = [
            models.Index(fields=['-author'])
        ]
    def __str__(self):
        return f'{self.author}, {self.title}'
    
class Section(models.Model):
    header = models.CharField(max_length=50, help_text='Section Header')
    body = models.TextField()
    order = models.IntegerField(help_text='Order #')
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name= 'sections'
    )
    class Meta:
        ordering = ['-order']
        indexes = [
            models.Index(fields = ['-order'])
        ]
    def __str__(self):
        return self.header