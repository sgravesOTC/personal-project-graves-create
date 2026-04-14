from django.contrib import admin
from .models import ForagingReport, ForagingReportSpecies
import csv
import datetime
from django.http import HttpResponse

# Register your models here.
class ForagingReportSpeciesInline(admin.TabularInline):
    model = ForagingReportSpecies
    raw_id_fields = ['species']

def export_to_csv(modeladmin, request, queryset, filename='foraging_reports.csv'):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    writer = csv.writer(response)

    writer.writerow(['ID', 'User', 'Location', 'Date Foraged', 'Notes', 'Species Count'])

    for report in queryset:
        writer.writerow([
            report.id,
            report.user.username,
            report.location,
            report.date_foraged.strftime('%Y-%m-%d'),
            report.notes,
            report.get_species_count(),
        ])

    return response
export_to_csv.short_description = 'Export selected reports to CSV'

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
    actions = [export_to_csv]

