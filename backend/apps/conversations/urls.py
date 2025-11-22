from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TopicViewSet, ConversationSessionViewSet

router = DefaultRouter()
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'sessions', ConversationSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]
