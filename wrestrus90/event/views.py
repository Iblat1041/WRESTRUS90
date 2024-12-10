from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from core.utils_template import menu_event
from core.Mixins import DataMixin


from .models import Event
from .forms import AddPostForm


class EventHome(ListView):
    template_name = 'event/index_event.html'
    context_object_name = 'posts'

    extra_context = {'title': 'Главная страница',
                     'cat_selected': 0,
                     'menu': menu_event,
                     }

    def get_queryset(self):
        return Event.objects.all()


class PostEvent(DetailView):
    model = Event
    template_name = 'event/post_event.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['post'].title
        context['menu'] = menu_event
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Event.objects, slug=self.kwargs[self.slug_url_kwarg])


class AddPostEvent(CreateView):
    form_class = AddPostForm
    template_name = 'event/add_post_event.html'

    extra_context = {
        'menu': menu_event,
        'title': 'Добавление меропртятия',
    }


class EventCategory(ListView):
    template_name = 'event/index_event.html'
    context_object_name = 'posts'
    allow_empty = False # при пустом списке ген исключение 404


    def get_queryset(self) -> QuerySet[Any]:
        return Event.objects.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cat = context['posts'][0].cat
        context['cat_model'] = 'event_model' 
        context['title'] = 'Категория' + cat.name
        context['cat_selected'] = cat.id
        return context
