from django.contrib import admin
from event.models import Event, CategoryEvent


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = fields = ['title', 'slug', 'content', 'cat']

@admin.register(CategoryEvent)
class CategoryAdmin(admin.ModelAdmin):
    list_display = fields = ['name', 'slug',]