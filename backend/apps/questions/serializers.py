from rest_framework import serializers
from .models import Question, QuestionCategory


class QuestionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'category', 'category_name', 'difficulty', 'position_type', 
                  'time_limit', 'audio_file', 'is_active', 'created_by', 'created_by_username',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'audio_file']


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['text', 'category', 'difficulty', 'position_type', 'time_limit', 'is_active']
    
    def create(self, validated_data):
        # Set created_by from request user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
