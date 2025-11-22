from rest_framework import serializers
from .models import Topic, ConversationSession, ConversationMessage, ConversationFeedback


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'difficulty', 'icon', 'color', 
                  'is_active', 'conversation_count', 'created_at']
        read_only_fields = ['id', 'conversation_count', 'created_at']


class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = ['id', 'session', 'role', 'text', 'audio_file', 'duration', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ConversationSessionSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    messages = ConversationMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ConversationSession
        fields = ['id', 'user', 'topic', 'topic_name', 'status', 'started_at', 'ended_at',
                  'duration', 'message_count', 'user_message_count', 'total_speaking_time', 'messages']
        read_only_fields = ['id', 'user', 'started_at', 'ended_at', 'duration', 
                           'message_count', 'user_message_count', 'total_speaking_time']


class ConversationSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationSession
        fields = ['id', 'topic']
    
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
