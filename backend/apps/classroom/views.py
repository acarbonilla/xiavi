from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ClassroomSession, ClassroomMessage
from .serializers import ClassroomSessionSerializer, ClassroomMessageSerializer
from services.gemini_service import GeminiService

class ClassroomSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ClassroomSession.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        session = self.get_object()
        user_message_text = request.data.get('message')
        
        if not user_message_text:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Save user message
        ClassroomMessage.objects.create(
            session=session,
            role='user',
            text=user_message_text
        )

        # Generate AI response
        try:
            gemini_service = GeminiService()
            # Get history
            history = session.messages.order_by('created_at')
            history_list = [{'role': msg.role, 'text': msg.text} for msg in history]
            
            response_data = gemini_service.generate_classroom_response(
                topic=session.topic.name if session.topic else "General Communication",
                conversation_history=history_list,
                user_message=user_message_text
            )
            
            # Save AI message
            ai_message = ClassroomMessage.objects.create(
                session=session,
                role='ai',
                text=response_data.get('response', ''),
                correction=response_data.get('correction') or '',
                explanation=response_data.get('explanation') or ''
            )
            
            return Response(ClassroomMessageSerializer(ai_message).data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
