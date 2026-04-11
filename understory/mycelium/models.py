from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# ================== MYCELIUM APP ==================
# This app tracks user activity throughout the platform (activity feed/timeline).
# Uses Django's ContentType framework for generic relationships to any model.


class Action(models.Model):
    """Activity log entry capturing user actions across the platform.
    
    Uses Django's content type framework (GenericForeignKey) to link actions
    to any model (Article, Specimen, etc.) without needing to know the specific type.
    
    This enables a unified activity feed showing all user actions:
    - 'spotted' an article
    - 'collected' a specimen
    - 'updated' a specimen
    
    Attributes:
        user: User who performed the action
        verb: String describing the action type ('spotted', 'collected', etc.)
        content_type: ContentType of the target object (Article, Specimen, etc.)
        object_id: ID of the target object
        target: GenericForeignKey combining content_type and object_id
        created: When the action occurred
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name = 'actions'
    )

    verb = models.CharField(max_length=255)

    # Generic foreign key components - allow linking to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null = True,
        blank = True
    )

    object_id = models.PositiveIntegerField(null=True, blank=True)
    # GenericForeignKey combines content_type + object_id to reference any model instance
    target = GenericForeignKey('content_type', 'object_id')

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']  # Newest actions first for activity feeds
        indexes = [
            models.Index(fields = ['-created']),
            models.Index(fields = ['content_type', 'object_id']),
        ]

    def __str__(self):
        return f'{self.user} {self.verb} {self.target}'

