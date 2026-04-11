from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse

# Create your models here.
class Specimen(models.Model):
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name = 'sporeprint_collected'
    )

    spotted_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='sporeprint_spotted',
        blank=True
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(
        max_length=250,
        blank = True
    )

    source_url = models.URLField()

    image = models.ImageField(upload_to='specimens/%Y/%m/%d/')

    description = models.TextField(blank = True)

    collected_on = models.DateField(auto_now_add=True)

    total_spots = models.PositiveIntegerField(default = 0)

    class Meta:
        ordering = ['-collected_on']
        indexes = [
            models.Index(fields=['-collected_on']),
            models.Index(fields=['-total_spots']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse(
            'sporeprint:specimen_detail',
            args = [self.id, self.slug]
        )
    