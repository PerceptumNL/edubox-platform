from django.conf.urls import url, include
from rest_framework import routers

from .views import LearningUnitViewSet

router = routers.DefaultRouter()
router.register(r'learning-units', LearningUnitViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
