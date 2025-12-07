from django.db import models
from django.utils import timezone
from services.voice_config import VOICE_CHOICES


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
        ('incomplete', 'Incomplete'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='conversations')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, related_name='sessions')
    scenario = models.ForeignKey('training.Scenario', on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0, help_text='Duration in seconds')
    message_count = models.IntegerField(default=0)
    user_message_count = models.IntegerField(default=0)
    total_speaking_time = models.IntegerField(default=0, help_text='User speaking time in seconds')
    voice_preference = models.CharField(
        max_length=20,
        choices=VOICE_CHOICES,
        null=True,
        blank=True,
        help_text='Voice preference for this session (overrides user profile default)'
    )


    # ADD THESE:
    conversation_memory = models.JSONField(default=list)
    emotion_trend = models.JSONField(default=list)
    conversation_depth = models.IntegerField(default=0)
    
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
        try:
            if hasattr(self.user, 'learner_profile'):
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
        except Exception as e:
            # Log error but don't fail the transaction
            print(f"Error updating profile stats: {e}")
    
    def mark_incomplete(self):
        """Mark conversation as incomplete (not finished)."""
        self.status = 'incomplete'
        self.ended_at = timezone.now()
        self.duration = int((self.ended_at - self.started_at).total_seconds())
        self.save()
        # Note: Does NOT update profile stats (only completed conversations count)


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
    
    # Filler Word Detection
    filler_word_count = models.IntegerField(default=0, help_text='Total filler words used')
    filler_word_rate = models.FloatField(default=0.0, help_text='Filler words per minute')
    filler_words_breakdown = models.JSONField(default=dict, help_text='Count by filler word type')
    
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
        try:
            if hasattr(self.session.user, 'learner_profile'):
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
        except Exception as e:
            print(f"Error updating profile skills: {e}")


class DocumentUpload(models.Model):
    """
    Uploaded documents for conversation context (RAG).
    Max 5 documents per session, session-specific only.
    """
    FILE_TYPE_CHOICES = (
        ('pdf', 'PDF'),
        ('txt', 'Text'),
    )
    
    session = models.ForeignKey(
        ConversationSession, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    file = models.FileField(upload_to='conversations/documents/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    file_size = models.IntegerField(help_text='Size in bytes')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, help_text='Error message if processing failed')
    chunk_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'document_uploads'
        verbose_name = 'Document Upload'
        verbose_name_plural = 'Document Uploads'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} ({self.get_file_type_display()}) - {self.session}"


class DocumentChunk(models.Model):
    """
    Text chunks with vector embeddings for RAG retrieval.
    Chunks are created during document processing.
    """
    document = models.ForeignKey(
        DocumentUpload, 
        on_delete=models.CASCADE, 
        related_name='chunks'
    )
    chunk_index = models.IntegerField(help_text='Sequential index of chunk in document')
    text = models.TextField(help_text='Chunk text content')
    embedding = models.JSONField(help_text='768-dimensional vector embedding as JSON array')
    token_count = models.IntegerField(default=0, help_text='Approximate token count')
    
    class Meta:
        db_table = 'document_chunks'
        verbose_name = 'Document Chunk'
        verbose_name_plural = 'Document Chunks'
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
    
    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document.filename}"
