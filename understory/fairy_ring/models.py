from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.
    
class ForagerConnection(models.Model):

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
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

        constraints = [
            models.UniqueConstraint(
                fields=['forager_from','forager_to'],
                name = 'unique_forager_connection'
            )
        ]

    def __str__(self):
        return f'{self.forager_from} follows {self.forager_to}'
    
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    birthday = models.DateField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        blank = True
    )

    def __str__(self):
        return f'Profile of {self.user.username}'