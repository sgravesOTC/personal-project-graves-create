from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
class Action(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name = 'actions'
    )

    verb = models.CharField(max_length=255)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null = True,
        blank = True
    )

    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields = ['-created']),
            models.Index(fields = ['content_type', 'object_id']),
        ]

    def __str__(self):
        return f'{self.user} {self.verb} {self.target}'

