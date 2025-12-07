from rest_framework import serializers
from .models import Topic, ConversationSession, ConversationMessage, ConversationFeedback, DocumentUpload, DocumentChunk


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'difficulty', 'icon', 'color', 
                  'is_active', 'conversation_count', 'created_at']
        read_only_fields = ['id', 'conversation_count', 'created_at']


class ConversationMessageSerializer(serializers.ModelSerializer):
    referenced_documents = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        read_only=True,
        help_text='Filenames of documents referenced in AI response'
    )
    
    class Meta:
        model = ConversationMessage
        fields = ['id', 'session', 'role', 'text', 'audio_file', 'duration', 'timestamp', 'referenced_documents']
        read_only_fields = ['id', 'timestamp']


class DocumentChunkSerializer(serializers.ModelSerializer):
    """Serializer for document chunks (mainly for debugging)."""
    class Meta:
        model = DocumentChunk
        fields = ['id', 'chunk_index', 'text', 'token_count']
        read_only_fields = ['id']


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload."""
    file_size_kb = serializers.SerializerMethodField()
    chunk_count = serializers.IntegerField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = DocumentUpload
        fields = ['id', 'session', 'file', 'filename', 'file_type', 'file_size', 
                  'file_size_kb', 'uploaded_at', 'processed', 'processing_error', 'chunk_count']
        read_only_fields = ['id', 'filename', 'file_type', 'file_size', 'uploaded_at', 
                           'processed', 'processing_error', 'chunk_count']
    
    def get_file_size_kb(self, obj):
        """Return file size in KB."""
        return round(obj.file_size / 1024, 1)
    
    def validate(self, data):
        """
        Validate document upload:
        - Max 5 documents per session
        - Max 10MB file size
        - Only PDF or TXT files
        """
        file = data.get('file')
        session = data.get('session')
        
        if not file:
            raise serializers.ValidationError("No file provided")
        
        # Check file size (50MB max)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if file.size > max_size:
            raise serializers.ValidationError(f"File size exceeds 50MB limit. Your file: {file.size / 1024 / 1024:.1f}MB")
        
        # Check file type
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in ['pdf', 'txt']:
            raise serializers.ValidationError(f"Unsupported file type: .{file_extension}. Only PDF and TXT files are allowed.")
        
        # Check document count per session (max 5)
        if session:
            existing_count = DocumentUpload.objects.filter(session=session).count()
            if existing_count >= 5:
                raise serializers.ValidationError("Maximum 5 documents per conversation session")
        
        return data


class ConversationSessionSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    messages = ConversationMessageSerializer(many=True, read_only=True)
    documents = DocumentUploadSerializer(many=True, read_only=True)
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationSession
        fields = ['id', 'user', 'topic', 'topic_name', 'status', 'started_at', 'ended_at',
                  'duration', 'message_count', 'user_message_count', 'total_speaking_time', 
                  'voice_preference', 'messages', 'documents', 'document_count']
        read_only_fields = ['id', 'user', 'started_at', 'ended_at', 'duration', 
                           'message_count', 'user_message_count', 'total_speaking_time']
    
    def get_document_count(self, obj):
        """Return number of documents in session."""
        return obj.documents.count()


class ConversationSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationSession
        fields = ['id', 'topic', 'voice_preference']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        session = ConversationSession.objects.create(**validated_data)
        
        # Update topic conversation count
        if session.topic:
            session.topic.conversation_count += 1
            session.topic.save()
        
        return session


class ConversationFeedbackSerializer(serializers.ModelSerializer):
    session_id = serializers.IntegerField(source='session.id', read_only=True)
    topic_name = serializers.CharField(source='session.topic.name', read_only=True)
    
    class Meta:
        model = ConversationFeedback
        fields = ['id', 'session', 'session_id', 'topic_name', 'overall_score', 
                  'clarity_score', 'fluency_score', 'vocabulary_score', 'grammar_score',
                  'confidence_score', 'engagement_score', 'feedback_text', 'strengths',
                  'improvements', 'tips', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserMessageSerializer(serializers.Serializer):
    """Serializer for user audio message upload."""
    audio_file = serializers.FileField(required=True)
    duration = serializers.IntegerField(required=True)

