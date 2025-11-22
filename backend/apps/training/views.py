from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import TrainingSession, TrainingFeedback
from .serializers import TrainingSessionSerializer, TrainingSessionCreateSerializer, TrainingFeedbackSerializer
from services.deepgram_service import DeepgramService
from services.gemini_service import GeminiService
from django.utils import timezone


class TrainingSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for training sessions.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TrainingSession.objects.filter(applicant=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TrainingSessionCreateSerializer
        return TrainingSessionSerializer
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark training session as completed.
        """
        session = self.get_object()
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()
        return Response({'message': 'Training session completed'})


class TrainingFeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for training feedback.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = TrainingFeedbackSerializer
    
    def get_queryset(self):
        return TrainingFeedback.objects.filter(session__applicant=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate instant AI feedback for a training video.
        """
        session_id = request.data.get('session_id')
        video_file = request.FILES.get('video_file')
        
        if not session_id or not video_file:
            return Response(
                {'error': 'session_id and video_file are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = TrainingSession.objects.get(id=session_id, applicant=request.user)
            
            # Save video temporarily
            feedback = TrainingFeedback.objects.create(
                session=session,
                video_file=video_file
            )
            
            # Transcribe with Deepgram
            deepgram_service = DeepgramService()
            transcript_data = deepgram_service.transcribe_video(feedback.video_file.path)
            feedback.transcript = transcript_data['text']
            
            # Generate feedback with Gemini
            gemini_service = GeminiService()
            feedback_data = gemini_service.generate_training_feedback(
                question=session.question.text,
                transcript=feedback.transcript
            )
            
            feedback.score = feedback_data['score']
            feedback.feedback = feedback_data['feedback']
            feedback.tips = feedback_data['tips']
            feedback.save()
            
            serializer = TrainingFeedbackSerializer(feedback)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except TrainingSession.DoesNotExist:
            return Response(
                {'error': 'Training session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
