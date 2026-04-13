from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import ForagingReport
from mycelium.models import Action

@receiver(post_save, sender=ForagingReport)
def log_report_created(sender, instance, created, **kwargs):
    """
    When a new ForagingReport is saved for the first time, automatically log it as an Action in the mycelium activity feed.
    """

    if created:
        Action.objects.create(
            user = instance.user,
            verb = 'filled a foraging report at',
            target=instance
        )