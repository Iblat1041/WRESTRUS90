from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('events/', views.events, name='events'),
    path('profile/', views.profile, name='profile'),
    path('contact/', views.contact, name='contact'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
]