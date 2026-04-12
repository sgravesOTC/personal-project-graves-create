from django.contrib import admin
from .models import ForagingReport, ForagingReportSpecies

# Register your models here.
class ForagingReportSpeciesInline(admin.TabularInline):
    model = ForagingReportSpecies
    raw_id_fields = ['species']

@admin.register(ForagingReport)
class ForagingReportAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'location',
        'date_foraged',
        'created'
    ]
    list_filter = ['created','date_foraged']
    inlines = [ForagingReportSpeciesInline]