from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from wrestrus90 import settings
from main_page.views import page_not_found 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_page.urls')),
    path('users/', include('users.urls', namespace="users")),
    path("api/", include("api.urls")),
    path('competition/', include('competition.urls')),
    path('event/', include('event.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = page_not_found