from rest_framework import serializers
from .models import Interview, InterviewQuestion
from apps.questions.serializers import QuestionSerializer


class InterviewQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    question_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = InterviewQuestion
        fields = ['id', 'question', 'question_id', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class InterviewSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    interview_questions = InterviewQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Interview
        fields = ['id', 'applicant', 'applicant_name', 'position_type', 'position_title', 
                  'status', 'scheduled_at', 'started_at', 'completed_at', 'interview_questions',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'started_at', 'completed_at']


class InterviewCreateSerializer(serializers.ModelSerializer):
    question_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Interview
        fields = ['position_type', 'position_title', 'scheduled_at', 'question_ids']
    
    def create(self, validated_data):
        question_ids = validated_data.pop('question_ids', [])
        validated_data['applicant'] = self.context['request'].user
        interview = Interview.objects.create(**validated_data)
        
        # Create interview questions
        for idx, question_id in enumerate(question_ids):
            InterviewQuestion.objects.create(
                interview=interview,
                question_id=question_id,
                order=idx
            )
        
        return interview
