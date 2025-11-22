from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Interview, InterviewQuestion
from .serializers import InterviewSerializer, InterviewCreateSerializer
from apps.core.permissions import IsHRUser
from django.utils import timezone


class InterviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing interviews.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'position_type']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_hr:
            return Interview.objects.all()
        return Interview.objects.filter(applicant=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InterviewCreateSerializer
        return InterviewSerializer
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """
        Get all questions for an interview.
        """
        interview = self.get_object()
        questions = interview.interview_questions.all()
        from apps.interviews.serializers import InterviewQuestionSerializer
        serializer = InterviewQuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Mark interview as started.
        """
        interview = self.get_object()
        if interview.status == 'pending':
            interview.status = 'in_progress'
            interview.started_at = timezone.now()
            interview.save()
            return Response({'message': 'Interview started'})
        return Response(
            {'error': 'Interview cannot be started'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark interview as completed.
        """
        interview = self.get_object()
        if interview.status == 'in_progress':
            interview.status = 'completed'
            interview.completed_at = timezone.now()
            interview.save()
            return Response({'message': 'Interview completed'})
        return Response(
            {'error': 'Interview cannot be completed'},
            status=status.HTTP_400_BAD_REQUEST
        )
