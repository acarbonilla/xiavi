from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Question, QuestionCategory
from .serializers import QuestionSerializer, QuestionCreateSerializer, QuestionCategorySerializer
from apps.core.permissions import IsHRUser


class QuestionCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for question categories.
    """
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHRUser()]
        return super().get_permissions()


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for questions with filtering by position type, difficulty, and category.
    """
    queryset = Question.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['position_type', 'difficulty', 'category']
    search_fields = ['text']
    ordering_fields = ['created_at', 'difficulty']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return QuestionCreateSerializer
        return QuestionSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHRUser()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # HR can see all questions, applicants only see active ones
        if not self.request.user.is_hr:
            queryset = queryset.filter(is_active=True)
        
        return queryset
