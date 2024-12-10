from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.views.generic import ListView

from core.utils_template import menu_wrestrus_home

from competition.models import Competition


class HomePage(ListView):
    template_name = 'landing_page/wrestrus_home.html'
    context_object_name = 'posts'

    extra_context = {'title': 'Главная страница',
                     'cat_selected': 0,
                     'menu': menu_wrestrus_home,
                     }

    def get_queryset(self):
        return Competition.objects.all()
    

def HomeFederation(request):
    return render(request, 'landing_page/federation.html', {'title': 'О нас..', 'menu': menu_wrestrus_home,})


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена, работает функция исключения</h1>")
