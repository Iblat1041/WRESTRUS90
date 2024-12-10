from django.urls import path
from . import views

urlpatterns = [
    path('',
        views.CompetitionHome.as_view(),
        name='competition_home'
        ),
    path('post_competition/<slug:post_slug>/',
        views.ShowPostCompetition.as_view(),
        name='post_competition'
        ),
    path(
        'category/<slug:cat_slug>/',
        views.CompetitionCategory.as_view(),
        name='category_competition'
        ),
    path('add_post_competition/',
        views.AddPostCompetition.as_view(),
        name='add_post_competition'
        ),
    path('about/',
        views.about,
        name='about'
        ),
]
