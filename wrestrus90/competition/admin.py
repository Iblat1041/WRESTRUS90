from django.contrib import admin, messages

from .models import Competition, CategoryCompetition


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = fields = ['title', 'slug', 'cat', 'content']


@admin.register(CategoryCompetition)
class CategoryAdmin(admin.ModelAdmin):
    list_display = fields = ['name', 'slug']
