from django.db import models
from django.utils import timezone


class Topic(models.Model):
    """
    Conversation topics for learning.
    """
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    icon = models.CharField(max_length=50, default='message-circle', help_text='Lucide icon name')
    color = models.CharField(max_length=20, default='blue', help_text='Color theme')
    is_active = models.BooleanField(default=True)
    conversation_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'topics'
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['difficulty', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_difficulty_display()})"


class ConversationSession(models.Model):
    """
    A conversation session between user and AI.
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='conversations')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, related_name='sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0, help_text='Duration in seconds')
    message_count = models.IntegerField(default=0)
    user_message_count = models.IntegerField(default=0)
    total_speaking_time = models.IntegerField(default=0, help_text='User speaking time in seconds')
    
    class Meta:
        db_table = 'conversation_sessions'
        verbose_name = 'Conversation Session'
        verbose_name_plural = 'Conversation Sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.topic.name if self.topic else 'No Topic'} ({self.status})"
    
    def end_conversation(self):
        """Mark conversation as completed and calculate duration."""
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.duration = int((self.ended_at - self.started_at).total_seconds())
        self.save()
        
        # Update user profile
        profile = self.user.learner_profile
        profile.total_conversations += 1
        profile.total_speaking_time += self.total_speaking_time
        profile.update_streak(self.ended_at.date())
        
        # Update topics covered
        if self.topic:
            topics_covered = profile.topics_covered or {}
            topic_name = self.topic.name
            topics_covered[topic_name] = topics_covered.get(topic_name, 0) + 1
            profile.topics_covered = topics_covered
            profile.save()


class ConversationMessage(models.Model):
    """
    Individual messages in a conversation.
    """
    ROLE_CHOICES = (
        ('user', 'User'),
        ('ai', 'AI'),
    )
    
    session = models.ForeignKey(ConversationSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField(help_text='Message text (transcript for user, response for AI)')
    audio_file = models.FileField(upload_to='conversations/audio/', null=True, blank=True, 
                                   help_text='Audio file for user messages')
    duration = models.IntegerField(default=0, help_text='Audio duration in seconds')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation_messages'
        verbose_name = 'Conversation Message'
        verbose_name_plural = 'Conversation Messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_role_display()}: {self.text[:50]}..."
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update session message count
        self.session.message_count = self.session.messages.count()
        self.session.user_message_count = self.session.messages.filter(role='user').count()
        
        # Update total speaking time
        if self.role == 'user' and self.duration > 0:
            self.session.total_speaking_time += self.duration
        
        self.session.save()


class ConversationFeedback(models.Model):
    """
    AI-generated feedback for completed conversations.
    """
    session = models.OneToOneField(ConversationSession, on_delete=models.CASCADE, related_name='feedback')
    overall_score = models.FloatField(default=0.0, help_text='Overall score out of 100')
    clarity_score = models.FloatField(default=0.0, help_text='Pronunciation and clarity')
    fluency_score = models.FloatField(default=0.0, help_text='Speaking fluency and pace')
    vocabulary_score = models.FloatField(default=0.0, help_text='Vocabulary richness')
    grammar_score = models.FloatField(default=0.0, help_text='Grammar accuracy')
    confidence_score = models.FloatField(default=0.0, help_text='Speaking confidence')
    engagement_score = models.FloatField(default=0.0, help_text='Conversation engagement')
    
    feedback_text = models.TextField(blank=True, help_text='Detailed feedback')
    strengths = models.TextField(blank=True, help_text='What the user did well')
    improvements = models.TextField(blank=True, help_text='Areas for improvement')
    tips = models.TextField(blank=True, help_text='Actionable tips')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation_feedbacks'
        verbose_name = 'Conversation Feedback'
        verbose_name_plural = 'Conversation Feedbacks'
    
    def __str__(self):
        return f"Feedback: {self.session} - Score: {self.overall_score}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update user's skill scores in profile
        profile = self.session.user.learner_profile
        profile.skill_scores = {
            'clarity': self.clarity_score,
            'fluency': self.fluency_score,
            'vocabulary': self.vocabulary_score,
            'grammar': self.grammar_score,
            'confidence': self.confidence_score,
            'engagement': self.engagement_score,
        }
        profile.save()
