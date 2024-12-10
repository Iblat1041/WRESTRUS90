from django.urls import path, include

from .views import CompetitionViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'competition', CompetitionViewSet)


urlpatterns = [
    path('v1/', include(router.urls)),
]