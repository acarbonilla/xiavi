from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model for conversational learning platform.
    """
    LANGUAGE_LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    language_level = models.CharField(max_length=20, choices=LANGUAGE_LEVEL_CHOICES, default='beginner')
    native_language = models.CharField(max_length=50, default='English')
    target_language = models.CharField(max_length=50, default='English')
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_language_level_display()})"


class LearnerProfile(models.Model):
    """
    Extended profile for learners with progress tracking.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='learner_profile')
    bio = models.TextField(blank=True)
    total_conversations = models.IntegerField(default=0)
    total_speaking_time = models.IntegerField(default=0, help_text='Total speaking time in seconds')
    current_streak = models.IntegerField(default=0, help_text='Current daily streak')
    longest_streak = models.IntegerField(default=0, help_text='Longest daily streak')
    topics_covered = models.JSONField(default=dict, help_text='Topics and conversation counts')
    skill_scores = models.JSONField(default=dict, help_text='Latest skill scores')
    last_conversation_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'learner_profiles'
        verbose_name = 'Learner Profile'
        verbose_name_plural = 'Learner Profiles'
    
    def __str__(self):
        return f"Profile: {self.user.username}"
    
    def update_streak(self, conversation_date):
        """Update streak based on conversation date."""
        from datetime import timedelta
        
        if self.last_conversation_date:
            days_diff = (conversation_date - self.last_conversation_date).days
            if days_diff == 1:
                self.current_streak += 1
            elif days_diff > 1:
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_conversation_date = conversation_date
        self.save()
