from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, LearnerProfile


class LearnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerProfile
        fields = ['bio', 'total_conversations', 'total_speaking_time', 'current_streak', 
                  'longest_streak', 'topics_covered', 'skill_scores', 'last_conversation_date', 'preferred_voice']
        read_only_fields = ['total_conversations', 'total_speaking_time', 'current_streak', 
                           'longest_streak', 'last_conversation_date']


class UserSerializer(serializers.ModelSerializer):
    learner_profile = LearnerProfileSerializer(required=False)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'language_level',
                  'native_language', 'target_language', 'phone', 'learner_profile', 'created_at']
        read_only_fields = ['id', 'created_at']

    def update(self, instance, validated_data):
        learner_profile_data = validated_data.pop('learner_profile', None)
        
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update LearnerProfile fields
        if learner_profile_data:
            profile = instance.learner_profile
            for attr, value in learner_profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 
                  'language_level', 'native_language', 'target_language', 'phone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        
        # Create learner profile
        LearnerProfile.objects.create(user=user)
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
