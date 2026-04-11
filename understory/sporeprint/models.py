from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse

# ================== SPOREPRINT APP ==================
# This app manages user collections of mushroom specimens (field notes).
# Users can collect/upload mushroom photos with metadata and share them.
# Other users can spot (like) specimens to track what they've found.


class Specimen(models.Model):
    """A mushroom specimen collected and documented by a user.
    
    Represents a single mushroom sighting/collection with photographic evidence.
    Supports both uploaded images and URLs pointing to online sources.
    
    Attributes:
        collector: User who collected/documented this specimen
        spotted_by: Users who have marked they've seen this species
        title: Common or scientific name of the mushroom
        slug: URL-friendly identifier
        source_url: Optional URL where the mushroom data came from
        image: Photo of the specimen
        description: Notes about the specimen (habitat, notes, etc.)
        collected_on: Date the specimen was found
        total_spots: Cached count of users who spotted this specimen
    """
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
        ordering = ['-collected_on']  # Newest specimens first
        indexes = [
            models.Index(fields=['-collected_on']),  # Speed up chronological sorting
            models.Index(fields=['-total_spots']),  # Speed up popularity sorting
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not already set."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse(
            'sporeprint:specimen_detail',
            args = [self.id, self.slug]
        )
    