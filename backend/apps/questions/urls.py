from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, QuestionCategoryViewSet

router = DefaultRouter()
router.register(r'', QuestionViewSet, basename='question')
router.register(r'categories', QuestionCategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
