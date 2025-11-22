from rest_framework import serializers
from .models import TrainingSession, TrainingFeedback


class TrainingFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingFeedback
        fields = ['id', 'session', 'video_file', 'transcript', 'score', 'feedback', 'tips', 'created_at']
        read_only_fields = ['id', 'transcript', 'score', 'feedback', 'tips', 'created_at']


class TrainingSessionSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    feedbacks = TrainingFeedbackSerializer(many=True, read_only=True)
    
    class Meta:
        model = TrainingSession
        fields = ['id', 'applicant', 'question', 'question_text', 'status', 'feedbacks', 
                  'created_at', 'completed_at']
        read_only_fields = ['id', 'applicant', 'created_at', 'completed_at']


class TrainingSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = ['question']
    
    def create(self, validated_data):
        validated_data['applicant'] = self.context['request'].user
        return super().create(validated_data)
