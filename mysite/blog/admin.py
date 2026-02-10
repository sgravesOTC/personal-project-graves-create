from django.contrib import admin
from .models import Article,Reference,Section

# Article Admin to manage the article models
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title','slug','author','publish','status']
    list_filter = ['status','created','publish','author']
    search_fields = ['title','body']
    prepopulated_fields = {'slug':('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status','publish']

# Reference Admin to manage the reference Models
@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ['title','author','publish']
    list_filter = ['author','article']
    search_fields = ['title','body','author','article']
    ordering = ['article','author','publish']

# Section Admin to manage the section Models
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['header', 'article', 'order']
    list_filter = ['article']
    search_fields = ['header', 'body']
    ordering = ['article', 'order']