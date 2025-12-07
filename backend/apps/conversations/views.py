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
from .models import Topic, ConversationSession, ConversationMessage, ConversationFeedback, DocumentUpload
from .serializers import (
    TopicSerializer, ConversationSessionSerializer, ConversationSessionCreateSerializer,
    ConversationMessageSerializer, ConversationFeedbackSerializer, UserMessageSerializer,
    DocumentUploadSerializer
)
from services.deepgram_service import DeepgramService
from services.google_tts_service import GoogleTTSService
from services.gemini_service import GeminiService
from services.document_service import DocumentProcessor


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
        queryset = ConversationSession.objects.filter(user=self.request.user)
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
            # If asking for incomplete, exclude those that actually have feedback
            # This handles cases where a session has feedback but status wasn't updated
            if status_param == 'incomplete':
                queryset = queryset.filter(feedback__isnull=True)
                
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Self-healing: If session has feedback but status is not completed, mark it as completed
        try:
            if instance.feedback and instance.status != 'completed':
                logger.info(f"Auto-completing session {instance.id} because feedback exists")
                instance.status = 'completed'
                if not instance.ended_at:
                    instance.ended_at = instance.feedback.created_at
                instance.save()
        except ConversationFeedback.DoesNotExist:
            pass
            
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        """
        Delete session and decrement topic conversation count.
        """
        if instance.topic:
            instance.topic.conversation_count = max(0, instance.topic.conversation_count - 1)
            instance.topic.save()
        instance.delete()

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationSessionCreateSerializer
        return ConversationSessionSerializer
    
    @action(detail=False, methods=['post'])
    def start_conversation(self, request):
        """
        Start a new conversation with optional topic or scenario.
        """
        topic_id = request.data.get('topic_id')
        scenario_id = request.data.get('scenario_id')
        voice_id = request.data.get('voice_id')
        
        session_data = {
            'user': request.user,
        }
        
        # Add voice preference if provided
        if voice_id:
            session_data['voice_preference'] = voice_id
        
        initial_message = "Hello! I'm your English practice partner. What would you like to talk about today?"
        system_prompt = "You are a helpful language tutor helping learners practice English conversation."
        
        if scenario_id:
            from apps.training.models import Scenario
            try:
                scenario = Scenario.objects.get(id=scenario_id, is_active=True)
                session_data['scenario'] = scenario
                initial_message = scenario.initial_message
                system_prompt = scenario.system_prompt
            except Scenario.DoesNotExist:
                return Response(
                    {'error': 'Scenario not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif topic_id:
            try:
                topic = Topic.objects.get(id=topic_id, is_active=True)
                session_data['topic'] = topic
                topic.conversation_count += 1
                topic.save()
                initial_message = f"Let's talk about {topic.name}. {topic.description}"
                system_prompt = f"You are a helpful language tutor. The topic is {topic.name}."
            except Topic.DoesNotExist:
                return Response(
                    {'error': 'Topic not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create session
        session = ConversationSession.objects.create(**session_data)
        
        # Create initial AI message
        ConversationMessage.objects.create(
            session=session,
            role='ai',
            text=initial_message
        )
        
        serializer = ConversationSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for a conversation.
        """
        session = self.get_object()
        messages = session.messages.all()
        serializer = ConversationMessageSerializer(messages, many=True, context={'request': request})
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
            
            # Generate AI response with Gemini (RAG-enhanced)
            try:
                print("!!! DEBUG: Starting Gemini generation... !!!")
                logger.info("Generating AI response with Gemini")
                gemini_service = GeminiService()
                ai_response_data = gemini_service.generate_conversation_response(
                    topic=session.topic.name if session.topic else "General",
                    conversation_history=conversation_history,
                    user_message=transcript_data['text'],
                    session=session  # Pass session for RAG
                )
                # Extract response text and referenced documents
                ai_response_text = ai_response_data.get('response', ai_response_data.get('text', ''))
                referenced_docs = ai_response_data.get('referenced_documents', [])
                logger.info(f"AI response generated: {ai_response_text[:50]}...")
                if referenced_docs:
                    logger.info(f"Used documents: {', '.join(referenced_docs)}")
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
                
                # Determine voice to use: session preference > user profile preference > default
                from services.voice_config import get_voice_name, DEFAULT_VOICE
                voice_choice = session.voice_preference
                if not voice_choice:
                    # Fall back to user's profile preference
                    try:
                        if hasattr(session.user, 'learner_profile') and session.user.learner_profile:
                            voice_choice = session.user.learner_profile.preferred_voice
                        else:
                            voice_choice = DEFAULT_VOICE
                    except Exception as profile_error:
                        logger.warning(f"Could not get profile voice preference: {profile_error}")
                        voice_choice = DEFAULT_VOICE
                
                # Ensure we have a valid voice choice
                if not voice_choice:
                    voice_choice = DEFAULT_VOICE
                
                voice_name = get_voice_name(voice_choice)
                logger.info(f"Using voice: {voice_choice} ({voice_name})")
                
                tts_service = GoogleTTSService()
                audio_content = tts_service.generate_speech(ai_response_text, voice_name=voice_name)
                logger.info("TTS audio generated successfully")
                audio_hex = audio_content.hex()
            except Exception as e:
                logger.error(f"TTS generation failed: {str(e)}")
                logger.error(traceback.format_exc())
                # Continue without audio
            
            return Response({
                'user_message': ConversationMessageSerializer(user_message, context={'request': request}).data,
                'ai_message': ConversationMessageSerializer(ai_message, context={'request': request}).data,
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
            
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """
        End conversation and generate feedback.
        """
        session = self.get_object()
        
        if session.status != 'active':
            # Idempotency: If already ended, return success
            logger.info(f"Session {session.id} already ended. Returning success.")
            return Response({'message': 'Conversation already ended'})
        
        try:
            # End the conversation
            session.end_conversation()
            
            # Generate feedback if there are user messages
            if session.user_message_count > 0:
                try:
                    gemini_service = GeminiService()
                    messages = session.messages.all()
                    feedback_data = gemini_service.analyze_conversation(session, messages)
                    
                    # Get filler word stats from all user messages
                    all_user_text = ""
                    for msg in messages.filter(role='user'):
                        all_user_text += " " + msg.text
                    filler_stats = gemini_service._detect_filler_words(all_user_text, session.duration)
                    
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
                        tips=feedback_data.get('tips', ''),
                        filler_word_count=filler_stats['total_count'],
                        filler_word_rate=filler_stats['rate_per_minute'],
                        filler_words_breakdown=filler_stats['breakdown']
                    )
                    
                    # Save suggested vocabulary
                    suggested_vocab = feedback_data.get('suggested_vocabulary', [])
                    if suggested_vocab:
                        from apps.learning.models import VocabularyItem
                        for item in suggested_vocab:
                            try:
                                VocabularyItem.objects.get_or_create(
                                    user=request.user,
                                    word=item['word'],
                                    defaults={
                                        'definition': item['definition'],
                                        'example_sentence': item.get('example', ''),
                                        'translation': item.get('translation', ''),
                                        'source_session': session
                                    }
                                )
                            except Exception as e:
                                logger.error(f"Error saving vocabulary item {item.get('word')}: {e}")
                except Exception as e:
                    logger.error(f"Feedback generation failed: {str(e)}")
                    logger.error(traceback.format_exc())
                    
                    # Fallback: Create empty feedback so user doesn't get 404
                    try:
                        ConversationFeedback.objects.get_or_create(
                            session=session,
                            defaults={
                                'overall_score': 0.0,
                                'feedback_text': "AI feedback could not be generated at this time. Please try again later.",
                                'strengths': "N/A",
                                'improvements': "N/A",
                                'tips': "Please check your internet connection or try again later."
                            }
                        )
                    except Exception as fallback_error:
                        logger.error(f"Fallback feedback creation failed: {fallback_error}")
            else:
                # No user messages, create empty feedback
                try:
                    ConversationFeedback.objects.get_or_create(
                        session=session,
                        defaults={
                            'overall_score': 0.0,
                            'feedback_text': "No feedback available. The conversation was too short to analyze.",
                            'strengths': "N/A",
                            'improvements': "N/A",
                            'tips': "Try speaking more in your next conversation!"
                        }
                    )
                except Exception as e:
                    logger.error(f"Empty session feedback creation failed: {e}")
            
            return Response({'message': 'Conversation ended successfully'})
        
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            logger.error(traceback.format_exc())
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
            # Provide more informative error messages based on session status
            error_messages = {
                'active': 'This conversation is still active. End the conversation to receive feedback.',
                'incomplete': 'This conversation was marked as incomplete. Complete the conversation to receive feedback.',
                'completed': 'Feedback is not available for this conversation. It may not have been generated yet.'
            }
            error_message = error_messages.get(
                session.status,
                'Feedback not found for this conversation.'
            )
            
            return Response(
                {
                    'error': error_message,
                    'session_status': session.status,
                    'session_id': session.id,
                    'has_messages': session.message_count > 0
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def mark_incomplete(self, request, pk=None):
        """
        Mark conversation as incomplete (save for later).
        """
        session = self.get_object()
        
        if session.status != 'active':
            return Response(
                {'error': 'Only active conversations can be marked incomplete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session.mark_incomplete()
            return Response({'message': 'Conversation marked as incomplete'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def upload_document(self, request, pk=None):
        """
        Upload a document (PDF/TXT) to the conversation session for RAG.
        Max 5 documents per session, files up to 50MB.
        """
        session = self.get_object()
        
        # Check if session is active
        if session.status != 'active':
            return Response(
                {'error': 'Can only upload documents to active conversations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare data for serializer
        data = {
            'session': session.id,
            'file': file
        }
        
        serializer = DocumentUploadSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Extract file metadata
            filename = file.name
            file_extension = filename.split('.')[-1].lower()
            file_size = file.size
            
            # Create DocumentUpload instance
            document = DocumentUpload.objects.create(
                session=session,
                file=file,
                filename=filename,
                file_type=file_extension,
                file_size=file_size,
                processed=False
            )
            
            # Process document (extract, chunk, embed)
            logger.info(f"Processing document: {filename}")
            processor = DocumentProcessor()
            chunk_count, error_msg = processor.process_document(document)
            
            if error_msg:
                logger.error(f"Document processing failed: {error_msg}")
                return Response(
                    {'error': f'Document processing failed: {error_msg}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            logger.info(f"Document processed successfully: {chunk_count} chunks created")
            
            # Refresh from database to get updated fields
            document.refresh_from_db()
            serializer = DocumentUploadSerializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Document upload failed: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {'error': f'Document upload failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        Get all documents for a conversation session.
        """
        session = self.get_object()
        documents = session.documents.all()
        serializer = DocumentUploadSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'], url_path='documents/(?P<document_id>[^/.]+)')
    def delete_document(self, request, pk=None, document_id=None):
        """
        Delete a specific document by ID.
        """
        try:
            document = DocumentUpload.objects.get(id=document_id, session__user=request.user)
            
            # Delete file from storage
            if document.file:
                document.file.delete()
            
            # Delete document (cascades to chunks)
            document.delete()
            
            return Response({'message': 'Document deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        
        except DocumentUpload.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Document deletion failed: {str(e)}")
            return Response(
                {'error': f'Document deletion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get analytics data for progress tracking.
        Query params: days (default: 30)
        """
        days = int(request.query_params.get('days', 30))
        user = request.user
        
        # Get date range
        from datetime import timedelta
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get all completed sessions with feedback in date range
        sessions = ConversationSession.objects.filter(
            user=user,
            status='completed',
            started_at__date__gte=start_date,
            started_at__date__lte=end_date
        ).select_related('feedback').order_by('started_at')
        
        # Build skill progress data
        skill_data = []
        for session in sessions:
            try:
                feedback = session.feedback
                skill_data.append({
                    'date': session.started_at.date().isoformat(),
                    'overall': round(feedback.overall_score, 1),
                    'clarity': round(feedback.clarity_score, 1),
                    'fluency': round(feedback.fluency_score, 1),
                    'vocabulary': round(feedback.vocabulary_score, 1),
                    'grammar': round(feedback.grammar_score, 1),
                    'confidence': round(feedback.confidence_score, 1),
                    'engagement': round(feedback.engagement_score, 1),
                })
            except ConversationFeedback.DoesNotExist:
                continue
        
        # Get speaking time by week
        speaking_time_data = []
        current_date = start_date
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            week_sessions = ConversationSession.objects.filter(
                user=user,
                status='completed',
                started_at__date__gte=current_date,
                started_at__date__lte=week_end
            )
            total_minutes = sum(s.total_speaking_time for s in week_sessions) / 60.0
            speaking_time_data.append({
                'week_start': current_date.isoformat(),
                'minutes': round(total_minutes, 1),
                'conversations': week_sessions.count()
            })
            current_date = week_end + timedelta(days=1)
        
        return Response({
            'skill_progress': skill_data,
            'speaking_time': speaking_time_data,
            'total_conversations': sessions.count(),
        })
