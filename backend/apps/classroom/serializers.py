from rest_framework import serializers
from .models import ClassroomSession, ClassroomMessage
from apps.conversations.serializers import TopicSerializer

class ClassroomMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomMessage
        fields = ['id', 'role', 'text', 'correction', 'explanation', 'created_at']

class ClassroomSessionSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(read_only=True)
    topic_id = serializers.IntegerField(write_only=True)
    messages = ClassroomMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ClassroomSession
        fields = ['id', 'user', 'topic', 'topic_id', 'status', 'created_at', 'messages']
        read_only_fields = ['user', 'status', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        return ClassroomSession.objects.create(user=user, **validated_data)
