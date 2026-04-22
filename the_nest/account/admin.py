from django.contrib import admin
from .models import Profile, Child

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'pronouns_1', 'pronouns_2', 'onboarding_complete']
    raw_id_fields = ['user']

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'parent', 'pronouns_1', 'pronouns_2', 'age_range']
    raw_id_fields = ['parent']