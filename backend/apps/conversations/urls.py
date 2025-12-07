from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TopicViewSet, ConversationSessionViewSet
from .voice_views import VoiceViewSet

router = DefaultRouter()
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'sessions', ConversationSessionViewSet, basename='session')
router.register(r'voices', VoiceViewSet, basename='voice')

urlpatterns = [
    path('', include(router.urls)),
]
