from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainingSessionViewSet, TrainingFeedbackViewSet

router = DefaultRouter()
router.register(r'sessions', TrainingSessionViewSet, basename='session')
router.register(r'feedback', TrainingFeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
]
