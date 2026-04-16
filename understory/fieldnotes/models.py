from django.db import models
from django.conf import settings
from mycoguide.models import MushroomSpecies

# Create your models here.
class ForagingReport(models.Model):
    """
    A foraging report - captures who filed it, where they were, and when.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='foraging_reports'
    )
    location = models.CharField(max_length=250)
    date_foraged = models.DateField()
    notes = models.TextField(blank = True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return f'Report {self.id} by {self.user}'
    
    def get_species_count(self):
        """
        Returns the total number of species in this report.
        """

        return sum(item.quantity for item in self.items.all())
    
class ForagingReportSpecies(models.Model):
    """"
    An individual species entry within a foraging report.
    """
    # TextChoice fields for Species details
    class GrowthStage(models.TextChoices):
        BUTTON = 'BT', 'Button' # Very young, cap still closed
        PIN = 'PN', 'Pin' # Just emerging
        MATURE = 'MT', 'Mature' # Fully Developed
        PAST = 'PS','Past Prime' # Overripe/Decaying
    
    class Condition(models.TextChoices):
        FRESH = 'FR','Fresh'
        WEATHERED = 'WT', 'Weathered'
        DAMAGED = 'DM', 'Damaged'
        INEDIBLE = 'IN', 'Inedible'

    report = models.ForeignKey(
        ForagingReport,
        related_name='items',
        on_delete=models.CASCADE
    )
    species = models.ForeignKey(
        MushroomSpecies,
        related_name = 'report_items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=250, blank = True)

    # Observation Fields
    growth_stage = models.CharField(
        max_length=2,
        choices = GrowthStage.choices,
        blank = True # Makes this field optional
    )
    condition = models.CharField(
        max_length=2,
        choices = Condition.choices,
        blank = True
    )
    habitat_context = models.CharField(max_length=250, blank = True)

    def __str__(self):
        return f'{self.quantity}X {self.species.common_name}'
    
