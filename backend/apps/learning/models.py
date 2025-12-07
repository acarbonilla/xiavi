from django.db import models
from django.conf import settings

class VocabularyItem(models.Model):
    """
    Represents a vocabulary word that a user is learning.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vocabulary')
    word = models.CharField(max_length=100)
    definition = models.TextField()
    example_sentence = models.TextField(blank=True)
    translation = models.TextField(blank=True, help_text="Translation in user's native language (optional)")
    
    # Learning progress
    mastery_level = models.IntegerField(default=1, help_text="1: New, 2: Learning, 3: Reviewing, 4: Mastered, 5: Expert")
    review_count = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    
    # Metadata
    source_session = models.ForeignKey('conversations.ConversationSession', on_delete=models.SET_NULL, null=True, blank=True, related_name='vocabulary_items')
    created_at = models.DateTimeField(auto_now_add=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'vocabulary_items'
        verbose_name = 'Vocabulary Item'
        verbose_name_plural = 'Vocabulary Items'
        ordering = ['-created_at']
        unique_together = ['user', 'word']  # Prevent duplicate words for same user
    
    def __str__(self):
        return f"{self.word} ({self.user.username})"
