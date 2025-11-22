from rest_framework import serializers
from .models import VideoResponse, Transcript


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = ['id', 'text', 'confidence', 'word_count', 'processing_time', 'created_at']
        read_only_fields = ['id', 'word_count', 'created_at']


class VideoResponseSerializer(serializers.ModelSerializer):
    transcript = TranscriptSerializer(read_only=True)
    question_text = serializers.CharField(source='question.text', read_only=True)
    
    class Meta:
        model = VideoResponse
        fields = ['id', 'interview', 'question', 'question_text', 'video_file', 'duration', 
                  'file_size', 'status', 'transcript', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoResponse
        fields = ['interview', 'question', 'video_file', 'duration', 'file_size']
    
    def create(self, validated_data):
        validated_data['status'] = 'uploading'
        return super().create(validated_data)
