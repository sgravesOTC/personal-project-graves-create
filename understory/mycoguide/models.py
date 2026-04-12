from django.db import models
from django.urls import reverse

# Create your models here.

class MushroomGenus(models.Model):
    """
    Represents a genus (e.g. Amanita, Boletus).
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'genus'
        verbose_name_plural = 'genera'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('mycoguide:species_list_by_genus', args = [self.slug])
    
class MushroomSpecies(models.Model):
    """
    Represents a specific mushroom species (e.g. Death cap, King Bolete).
    """
    genus = models.ForeignKey(
        MushroomGenus,
        related_name='species',
        on_delete=models.CASCADE
    )
    common_name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='species/%Y/%m/%d', blank = True)
    description = models.TextField(blank=True)

    EDIBILITY_CHOICES = [
        ('edible','Edible'),
        ('caution','Edible with Caution'),
        ('inedible','Inedible'),
        ('toxic','Toxic'),
        ('deadly','Deadly')
    ]
    edibility = models.CharField(
        max_length=20,
        choices=EDIBILITY_CHOICES,
        default='inedible'
    )

    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['common_name']
        indexes = [
            models.Index(fields = ['id','slug']),
            models.Index(fields = ['common_name']),
            models.Index(fields = ['-created']),
        ]
        verbose_name_plural = 'species'

    def __str__(self):
        return self.common_name
    
    def get_absolute_url(self):
        return reverse('mycoguide:species_detail',args=[self.id, self.slug])
    
