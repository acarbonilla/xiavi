from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import VocabularyItem
from .serializers import VocabularyItemSerializer, VocabularyItemCreateSerializer

class VocabularyItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vocabulary items.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source_session', 'mastery_level']
    search_fields = ['word', 'definition']
    ordering_fields = ['created_at', 'mastery_level', 'last_reviewed_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return VocabularyItem.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VocabularyItemCreateSerializer
        return VocabularyItemSerializer
    
    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        """
        Mark a vocabulary item as reviewed.
        """
        item = self.get_object()
        item.review_count += 1
        item.last_reviewed_at = timezone.now()
        item.save()
        return Response({'status': 'reviewed'})
    
    @action(detail=True, methods=['post'])
    def update_mastery(self, request, pk=None):
        """
        Update mastery level based on quiz result (correct/incorrect).
        """
        item = self.get_object()
        correct = request.data.get('correct', False)
        
        if correct:
            item.times_correct += 1
            if item.mastery_level < 5:
                item.mastery_level += 1
        else:
            if item.mastery_level > 1:
                item.mastery_level -= 1
        
        item.review_count += 1
        item.last_reviewed_at = timezone.now()
        item.save()
        
        serializer = self.get_serializer(item)
        return Response(serializer.data)
