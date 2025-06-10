from django.shortcuts import render
from django.http import HttpResponse
from .models import News, ChildRegistration, Event
from .forms import ChildRegistrationForm

def index(request):
    news_list = News.objects.all()[:5]
    if request.method == 'POST':
        form = ChildRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Регистрация успешна!')
    else:
        form = ChildRegistrationForm()
    return render(request, 'index.html', {'news_list': news_list, 'form': form})

def events(request):
    events = Event.objects.all()
    return render(request, 'events.html', {'events': events})

def profile(request):
    registrations = ChildRegistration.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'profile.html', {'registrations': registrations})

def contact(request):
    message = None
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message_text = request.POST['message']
        # Здесь можно добавить отправку email или сохранение в базу
        message = f"Спасибо, {name}! Ваше сообщение отправлено."
    return render(request, 'contact.html', {'message': message})

def news_detail(request, news_id):
    news = News.objects.get(id=news_id)
    return render(request, 'news_detail.html', {'news': news})
