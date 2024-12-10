from django.urls import path
from .views import EventHome, PostEvent, AddPostEvent, EventCategory

urlpatterns = [
    path('',
        EventHome.as_view(), 
        name='event'
        ),
    path('post_event/<slug:post_slug>/',
        PostEvent.as_view(),
        name='post_event'
        ),
    path('add_post_event/', 
        AddPostEvent.as_view(), 
        name='add_post_event'
        ),
    path(
        'category_event/<slug:cat_slug>/',
        EventCategory.as_view(),
        name='category_event'
        ),
]