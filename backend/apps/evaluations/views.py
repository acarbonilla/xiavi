from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Evaluation, QuestionEvaluation
from .serializers import EvaluationSerializer
from services.gemini_service import GeminiService
from apps.interviews.models import Interview


class EvaluationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for evaluations.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EvaluationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_hr:
            return Evaluation.objects.all()
        return Evaluation.objects.filter(interview__applicant=user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate AI evaluation for an interview.
        """
        interview_id = request.data.get('interview_id')
        
        if not interview_id:
            return Response(
                {'error': 'interview_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            interview = Interview.objects.get(id=interview_id)
            
            # Check if evaluation already exists
            if hasattr(interview, 'evaluation'):
                return Response(
                    {'error': 'Evaluation already exists for this interview'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get all responses with transcripts
            responses = interview.responses.filter(status='completed', transcript__isnull=False)
            
            if not responses.exists():
                return Response(
                    {'error': 'No completed responses found for this interview'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate evaluation using Gemini
            gemini_service = GeminiService()
            evaluation_data = gemini_service.evaluate_interview(interview, responses)
            
            # Create evaluation
            evaluation = Evaluation.objects.create(
                interview=interview,
                overall_score=evaluation_data['overall_score'],
                communication_score=evaluation_data['communication_score'],
                content_score=evaluation_data['content_score'],
                confidence_score=evaluation_data['confidence_score'],
                clarity_score=evaluation_data['clarity_score'],
                feedback=evaluation_data['feedback'],
                strengths=evaluation_data['strengths'],
                improvements=evaluation_data['improvements']
            )
            
            # Create question evaluations
            for q_eval_data in evaluation_data.get('question_evaluations', []):
                QuestionEvaluation.objects.create(
                    evaluation=evaluation,
                    video_response_id=q_eval_data['video_response_id'],
                    score=q_eval_data['score'],
                    feedback=q_eval_data['feedback'],
                    key_points=q_eval_data.get('key_points', '')
                )
            
            # Update interview status
            interview.status = 'evaluated'
            interview.save()
            
            serializer = EvaluationSerializer(evaluation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Interview.DoesNotExist:
            return Response(
                {'error': 'Interview not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='interview/(?P<interview_id>[^/.]+)')
    def by_interview(self, request, interview_id=None):
        """
        Get evaluation by interview ID.
        """
        try:
            evaluation = Evaluation.objects.get(interview_id=interview_id)
            serializer = EvaluationSerializer(evaluation)
            return Response(serializer.data)
        except Evaluation.DoesNotExist:
            return Response(
                {'error': 'Evaluation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
