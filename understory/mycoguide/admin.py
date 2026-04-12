from django.contrib import admin
from .models import MushroomGenus, MushroomSpecies

# Register your models here.

@admin.register(MushroomGenus)
class MushroomGenusAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}

@admin.register(MushroomSpecies)
class MushroomSpeciesAdmin(admin.ModelAdmin):
    list_display = [
        'common_name',
        'scientific_name',
        'genus',
        'edibility',
        'available',
        'created',
        'updated',
    ]
    list_filter = ['available','edibility','created','updated']
    list_editable = ['edibility','available']
    prepopulated_fields = {'slug':('common_name',)}

