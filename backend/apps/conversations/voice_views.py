from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from services.voice_config import get_all_voices


class VoiceViewSet(viewsets.ViewSet):
    """
    ViewSet for voice configuration.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        Get all available voice options with metadata.
        """
        voices = get_all_voices()
        return Response({'voices': voices}, status=status.HTTP_200_OK)
