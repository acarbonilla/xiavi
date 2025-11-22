from rest_framework import serializers
from .models import Evaluation, QuestionEvaluation


class QuestionEvaluationSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='video_response.question.text', read_only=True)
    
    class Meta:
        model = QuestionEvaluation
        fields = ['id', 'video_response', 'question_text', 'score', 'feedback', 'key_points', 'created_at']
        read_only_fields = ['id', 'created_at']


class EvaluationSerializer(serializers.ModelSerializer):
    question_evaluations = QuestionEvaluationSerializer(many=True, read_only=True)
    interview_id = serializers.IntegerField(source='interview.id', read_only=True)
    applicant_name = serializers.CharField(source='interview.applicant.get_full_name', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = ['id', 'interview', 'interview_id', 'applicant_name', 'overall_score', 
                  'communication_score', 'content_score', 'confidence_score', 'clarity_score',
                  'feedback', 'strengths', 'improvements', 'question_evaluations',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
