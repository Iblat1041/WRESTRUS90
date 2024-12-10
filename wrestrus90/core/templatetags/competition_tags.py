from django import template
from django.db.models import Count
from django.shortcuts import render

from competition.models import CategoryCompetition
from event.models import CategoryEvent

register = template.Library()

cats_db = [
    {'id': 1, 'name': 'О нас'},
    {'id': 2, 'name': 'Соревнования'},
    {'id': 3, 'name': 'Мероприятия'},
    {'id': 3, 'name': 'Контакты'},
]


@register.inclusion_tag('competition/list_categories.html')
def show_cat_competition(cat_selected=0):
    cats_competition = CategoryCompetition.objects.all()
    return {'cats_competition': cats_competition, 
            'cat_selected': cat_selected
            }


@register.inclusion_tag('event/list_categories.html')
def show_cat_event(cat_selected=0):
    cats_event = CategoryEvent.objects.all()
    return {'cats_event': cats_event, 
            'cat_selected': cat_selected
            }
