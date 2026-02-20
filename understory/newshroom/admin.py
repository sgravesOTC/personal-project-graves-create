from django.contrib import admin
from .models import Article

# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title','slug','author','publish','status']
    list_filter = ['status','publish','author']
    search_fields = ['title','body']
    prepopulated_fields = {'slug':('title',)}
    date_hierarchy = 'publish'
    ordering = ['status','publish']
    show_facets = admin.ShowFacets.ALWAYS