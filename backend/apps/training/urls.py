from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainingSessionViewSet, TrainingFeedbackViewSet, ScenarioViewSet

router = DefaultRouter()
router.register(r'sessions', TrainingSessionViewSet, basename='training-session')
router.register(r'feedback', TrainingFeedbackViewSet, basename='training-feedback')
router.register(r'scenarios', ScenarioViewSet, basename='scenario')

urlpatterns = [
    path('', include(router.urls)),
]
