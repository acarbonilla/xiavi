from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassroomSessionViewSet

router = DefaultRouter()
router.register(r'sessions', ClassroomSessionViewSet, basename='classroom-sessions')

urlpatterns = [
    path('', include(router.urls)),
]
