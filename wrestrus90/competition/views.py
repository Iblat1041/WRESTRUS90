from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from .models import Competition
from django.shortcuts import render, redirect, get_object_or_404
from core.utils_template import menu_competition
from core.Mixins import DataMixin

from .forms import AddPostForm, UploadFileForm
from .models import Competition, CategoryCompetition


class CompetitionHome(ListView):
    template_name = 'competition/index.html'
    context_object_name = 'posts'

    extra_context = {'title': 'Главная страница',
                     'cat_selected': 0,
                     'menu': menu_competition,
                     }

    def get_queryset(self):
        return Competition.objects.all()


class ShowPostCompetition(DetailView):
    template_name = 'competition/post_competition.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['post'].title
        context['menu'] = menu_competition
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Competition, slug=self.kwargs[self.slug_url_kwarg])


class AddPostCompetition(LoginRequiredMixin, CreateView):
    form_class = AddPostForm
    template_name = 'competition/addpage.html'
    login_url = '/admin/' # перенаправляем неавторизованого пользователя

    extra_context = {
        'menu': menu_competition,
        'title': 'Добавление статьи',
    }


class CompetitionCategory(ListView):
    template_name = 'competition/index.html'
    context_object_name = 'posts'
    allow_empty = False # при пустом списке ген исключение 404

    def get_queryset(self) -> QuerySet[Any]:
        return Competition.objects.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cat = context['posts'][0].cat
        context['cat_model'] = 'competition_model'
        context['title'] = 'Категория' + cat.name
        context['menu'] = menu_competition
        context['cat_selected'] = cat.id
        return context


def about(request):
    return render(request, 'competition/about.html', {'title': 'О нас..', 'menu': menu_competition,})
    