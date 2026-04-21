from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Pronouns(models.TextChoices):
    """
    A selection of pronouns that can be used thorughout.
    """
    NONBINARY1 = 'NB1', 'They'
    NONBINARY2 = 'NB2', 'Them'
    FEMME1 = 'FM1','She'
    FEMME2 = 'FM2', 'Her'
    MASC1 = 'MA1', 'He'
    MASC2 = 'MA2', 'Him'
    NEO1 = 'NE1', 'Ze'
    NEO2 = 'NE2', 'Hir'
    OTHER = 'NEW', 'Other'

# Create your models here.
class Profile(models.Model):
    """
    Extends the built in user profile.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    bio = models.TextField()
    pronouns_1 = models.CharField(
        max_length=3,
        choices=Pronouns.choices,
        default=None,
        null=True,
        blank=True
    )
    pronouns_2 = models.CharField(
        max_length=3,
        choices=Pronouns.choices,
        default=None,
        null=True,
        blank=True
    )
    timezone = None # TODO
    onboarding_complete = models.BooleanField(default=False)

    privacy_level = None # TODO

class Child(models.Model):
    first_name = models.CharField(max_length=50)
    pronouns_1 = models.CharField(
        max_length=3,
        choices=Pronouns.choices,
        default=None,
        null=True,
        blank=True
    )
    pronouns_2 = models.CharField(
        max_length=3,
        choices=Pronouns.choices,
        default=None,
        null=True,
        blank=True
    )
    class AgeRange(models.TextChoices):
        YOUNG = '<10', 'Under 10'
        PRETEEN = '10-13', '10 to 13'
        TEEN = '14-17', '14 to 17'
        ADULT = '18+', '18 or older'

    age_range = models.CharField(
        choices = AgeRange.choices,
        default = None
    )
    parent = models.ForeignKey(
        Profile,
        related_name = 'child',
        on_delete=models.CASCADE
    )

class Action(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='actions',
        on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')

    class Meta:
        indexes = [models.Index(fields=['-created'])]
        ordering = ['-created']