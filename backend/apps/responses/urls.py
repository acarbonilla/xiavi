from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoResponseViewSet

router = DefaultRouter()
router.register(r'', VideoResponseViewSet, basename='response')

urlpatterns = [
    path('', include(router.urls)),
]
