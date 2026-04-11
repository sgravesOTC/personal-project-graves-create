from django.contrib import admin
from .models import Specimen

# Register your models here.
@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    list_display = ['title','collector','collected_on','total_spots']
    list_filter = ['collected_on']
    search_fields = ['title','description']
    prepopulated_fields = {'slug': ('title',)}