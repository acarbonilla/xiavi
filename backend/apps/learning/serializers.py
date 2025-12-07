from rest_framework import serializers
from .models import VocabularyItem

class VocabularyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyItem
        fields = ['id', 'word', 'definition', 'example_sentence', 'translation', 
                  'mastery_level', 'review_count', 'times_correct', 'created_at', 'last_reviewed_at']
        read_only_fields = ['id', 'created_at', 'last_reviewed_at', 'review_count', 'times_correct']

class VocabularyItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyItem
        fields = ['word', 'definition', 'example_sentence', 'translation']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
