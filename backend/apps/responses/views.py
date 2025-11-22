from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import VideoResponse, Transcript
from .serializers import VideoResponseSerializer, VideoUploadSerializer, TranscriptSerializer
from services.deepgram_service import DeepgramService


class VideoResponseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for video responses.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_hr:
            return VideoResponse.objects.all()
        return VideoResponse.objects.filter(interview__applicant=user)
    
    def get_serializer_class(self):
        if self.action == 'upload':
            return VideoUploadSerializer
        return VideoResponseSerializer
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Upload a video response.
        """
        serializer = VideoUploadSerializer(data=request.data)
        if serializer.is_valid():
            video_response = serializer.save()
            return Response(
                VideoResponseSerializer(video_response).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Trigger STT processing for a video response.
        """
        video_response = self.get_object()
        
        if video_response.status != 'uploading':
            return Response(
                {'error': 'Video is already being processed or completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update status
            video_response.status = 'processing'
            video_response.save()
            
            # Process with Deepgram
            deepgram_service = DeepgramService()
            transcript_data = deepgram_service.transcribe_video(video_response.video_file.path)
            
            # Create transcript
            Transcript.objects.create(
                video_response=video_response,
                text=transcript_data['text'],
                confidence=transcript_data.get('confidence', 0.0),
                processing_time=transcript_data.get('processing_time', 0.0)
            )
            
            # Update status
            video_response.status = 'completed'
            video_response.save()
            
            return Response({'message': 'Processing completed'})
        
        except Exception as e:
            video_response.status = 'failed'
            video_response.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        """
        Get transcript for a video response.
        """
        video_response = self.get_object()
        try:
            transcript = video_response.transcript
            serializer = TranscriptSerializer(transcript)
            return Response(serializer.data)
        except Transcript.DoesNotExist:
            return Response(
                {'error': 'Transcript not found'},
                status=status.HTTP_404_NOT_FOUND
            )
