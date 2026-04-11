from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# ================== FAIRY RING APP ==================
# This app handles user authentication, profiles, and social connections.
# It manages user following relationships and user profile information.


class ForagerConnection(models.Model):
    """Represents a "following" relationship between two foragers (users).
    
    When User A follows User B, a ForagerConnection is created with:
    - forager_from: User A (the follower)
    - forager_to: User B (the user being followed)
    
    Prevents duplicate follows using unique constraint.
    """

    forager_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follwoing'
    )

    forager_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers'        
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']  # Most recent follows first
        indexes = [
            models.Index(fields=['-created'])  # Speed up sorting recent activity
        ]
        # Prevent duplicate follows: same user cannot follow another user twice
        constraints = [
            models.UniqueConstraint(
                fields=['forager_from','forager_to'],
                name = 'unique_forager_connection'
            )
        ]

    def __str__(self):
        return f'{self.forager_from} follows {self.forager_to}'
    
class Profile(models.Model):
    """Extended user profile with optional biographical information.
    
    Extends Django's built-in User model with additional fields.
    One-to-one relationship ensures each user has exactly one profile.
    
    Attributes:
        user: Foreign key to User (one-to-one)
        birthday: Optional date of birth
        photo: Optional profile picture
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    birthday = models.DateField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='users/%Y/%m/%d/',  # Organize by year/month/day
        blank = True
    )

    def __str__(self):
        return f'Profile of {self.user.username}'