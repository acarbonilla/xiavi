from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
import traceback
import logging
import tempfile
import os

logger = logging.getLogger(__name__)
from .models import Topic, ConversationSession, ConversationMessage, ConversationFeedback
from .serializers import (
    TopicSerializer, ConversationSessionSerializer, ConversationSessionCreateSerializer,
    ConversationMessageSerializer, ConversationFeedbackSerializer, UserMessageSerializer
)
from services.deepgram_service import DeepgramService
from services.google_tts_service import GoogleTTSService
from services.gemini_service import GeminiService


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for conversation topics.
    """
    queryset = Topic.objects.filter(is_active=True)
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]


class ConversationSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for conversation sessions.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConversationSession.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationSessionCreateSerializer
        return ConversationSessionSerializer
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for a conversation.
        """
        session = self.get_object()
        messages = session.messages.all()
        serializer = ConversationMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def speak(self, request, pk=None):
        """
        User sends audio message, AI responds.
        """
        print(f"\n\n!!! DEBUG: SPEAK ENDPOINT HIT for session {pk} !!!")
        logger.info(f"=== SPEAK ENDPOINT CALLED for session {pk} ===")
        logger.info(f"Request data keys: {list(request.data.keys())}")
        logger.info(f"Request FILES: {list(request.FILES.keys())}")
        
        session = self.get_object()
        logger.info(f"Session retrieved: {session.id}, status: {session.status}")
        
        if session.status != 'active':
            logger.warning(f"Session {session.id} is not active: {session.status}")
            return Response(
                {'error': 'Conversation is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserMessageSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info("Serializer validation passed")
        
        temp_audio_path = None
        try:
            # Save user audio message
            audio_file = serializer.validated_data['audio_file']
            duration = serializer.validated_data['duration']
            
            # Validate audio file
            if audio_file.size == 0:
                logger.error(f"Empty audio file received for session {session.id}")
                return Response(
                    {'error': 'Empty audio file received. Please ensure your microphone is working.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Starting audio transcription for session {session.id}")
            logger.info(f"Audio file size: {audio_file.size} bytes, duration: {duration}s")
            logger.info(f"Audio file name: {audio_file.name}, content type: {audio_file.content_type}")
            
            # Transcribe with Deepgram
            print("!!! DEBUG: Starting Deepgram transcription... !!!")
            # For small files, Django keeps them in memory without a temporary_file_path()
            # We need to write them to a temp file first
            try:
                deepgram_service = DeepgramService()
                
                # Check if file has a temporary path (large files) or needs to be written (small files)
                if hasattr(audio_file, 'temporary_file_path'):
                    try:
                        audio_path = audio_file.temporary_file_path()
                        logger.info(f"Using temporary file path: {audio_path}")
                    except (AttributeError, NotImplementedError):
                        # File is in memory, need to write to temp file
                        audio_path = None
                else:
                    audio_path = None
                
                # If no path, write to temp file
                if not audio_path:
                    logger.info("File is in memory, writing to temporary file")
                    # Create temp file with .webm extension
                    fd, temp_audio_path = tempfile.mkstemp(suffix='.webm')
                    with os.fdopen(fd, 'wb') as tmp:
                        # Write uploaded file to temp file
                        for chunk in audio_file.chunks():
                            tmp.write(chunk)
                    audio_path = temp_audio_path
                    logger.info(f"Wrote to temporary file: {audio_path}")
                
                print(f"!!! DEBUG: Transcribing file: {audio_path} !!!")
                transcript_data = deepgram_service.transcribe_video(audio_path)
                print(f"!!! DEBUG: Transcription completed: {transcript_data.get('text', '')[:20]}... !!!")
                logger.info(f"Transcription completed: {transcript_data['text'][:50] if len(transcript_data['text']) > 50 else transcript_data['text']}...")
                
                # Check if transcription is empty
                if not transcript_data.get('text') or transcript_data['text'].strip() == '':
                    logger.warning(f"Empty transcription received for session {session.id}")
                    return Response(
                        {'error': 'No speech detected in audio. Please speak louder or check your microphone.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except Exception as e:
                print(f"!!! DEBUG: Deepgram failed: {e} !!!")
                traceback.print_exc()
                logger.error(f"Deepgram transcription failed: {str(e)}")
                logger.error(f"Exception type: {type(e).__name__}")
                logger.error(traceback.format_exc())
                return Response(
                    {'error': f'Transcription failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            finally:
                # Clean up temporary file if we created one
                if temp_audio_path and os.path.exists(temp_audio_path):
                    try:
                        os.unlink(temp_audio_path)
                        logger.info(f"Cleaned up temporary file: {temp_audio_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete temporary file {temp_audio_path}: {str(e)}")
            
            # Create user message
            user_message = ConversationMessage.objects.create(
                session=session,
                role='user',
                text=transcript_data['text'],
                audio_file=audio_file,
                duration=duration
            )
            
            # Get conversation history for context
            previous_messages = session.messages.order_by('timestamp')[:10]  # Last 10 messages
            conversation_history = [
                {'role': msg.role, 'text': msg.text}
                for msg in previous_messages
            ]
            
            # Generate AI response with Gemini
            try:
                print("!!! DEBUG: Starting Gemini generation... !!!")
                logger.info("Generating AI response with Gemini")
                gemini_service = GeminiService()
                ai_response_text = gemini_service.generate_conversation_response(
                    topic=session.topic.name if session.topic else "General",
                    conversation_history=conversation_history,
                    user_message=transcript_data['text']
                )
                logger.info(f"AI response generated: {ai_response_text[:50]}...")
            except Exception as e:
                print(f"!!! DEBUG: Gemini failed: {e} !!!")
                traceback.print_exc()
                logger.error(f"Gemini generation failed: {str(e)}")
                logger.error(traceback.format_exc())
                return Response(
                    {'error': f'AI response generation failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create AI message
            ai_message = ConversationMessage.objects.create(
                session=session,
                role='ai',
                text=ai_response_text
            )
            
            # Generate TTS audio for AI response
            audio_hex = None
            try:
                logger.info("Generating TTS audio")
                tts_service = GoogleTTSService()
                audio_content = tts_service.generate_speech(ai_response_text)
                logger.info("TTS audio generated successfully")
                audio_hex = audio_content.hex()
            except Exception as e:
                logger.error(f"TTS generation failed: {str(e)}")
                logger.error(traceback.format_exc())
                # Continue without audio
            
            return Response({
                'user_message': ConversationMessageSerializer(user_message).data,
                'ai_message': ConversationMessageSerializer(ai_message).data,
                'ai_audio': audio_hex,  # Send as hex string or None
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print(f"!!! DEBUG: UNEXPECTED ERROR: {e} !!!")
            traceback.print_exc()
            logger.error(f"Unexpected error in speak endpoint: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Clean up temp file if it exists
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
            
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """
        End conversation and generate feedback.
        """
        session = self.get_object()
        
        if session.status != 'active':
            return Response(
                {'error': 'Conversation is already ended'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # End the conversation
            session.end_conversation()
            
            # Generate feedback if there are user messages
            if session.user_message_count > 0:
                gemini_service = GeminiService()
                messages = session.messages.all()
                feedback_data = gemini_service.analyze_conversation(session, messages)
                
                # Create feedback
                ConversationFeedback.objects.create(
                    session=session,
                    overall_score=feedback_data['overall_score'],
                    clarity_score=feedback_data['clarity_score'],
                    fluency_score=feedback_data['fluency_score'],
                    vocabulary_score=feedback_data['vocabulary_score'],
                    grammar_score=feedback_data['grammar_score'],
                    confidence_score=feedback_data['confidence_score'],
                    engagement_score=feedback_data['engagement_score'],
                    feedback_text=feedback_data['feedback'],
                    strengths=feedback_data['strengths'],
                    improvements=feedback_data['improvements'],
                    tips=feedback_data.get('tips', '')
                )
            
            return Response({'message': 'Conversation ended successfully'})
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def feedback(self, request, pk=None):
        """
        Get feedback for a conversation.
        """
        session = self.get_object()
        try:
            feedback = session.feedback
            serializer = ConversationFeedbackSerializer(feedback)
            return Response(serializer.data)
        except ConversationFeedback.DoesNotExist:
            return Response(
                {'error': 'Feedback not found'},
                status=status.HTTP_404_NOT_FOUND
            )
