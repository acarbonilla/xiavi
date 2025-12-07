from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VocabularyItemViewSet

router = DefaultRouter()
router.register(r'vocabulary', VocabularyItemViewSet, basename='vocabulary')

urlpatterns = [
    path('', include(router.urls)),
]
