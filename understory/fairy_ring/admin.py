from django.contrib import admin
from .models import Profile, ForagerConnection

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','birthday','photo']
    raw_id_fields = ['user']

@admin.register(ForagerConnection)
class ForagerConnectionAdmin(admin.ModelAdmin):
    list_display = ['forager_from','forager_to','created']
    list_filter = ['created']

