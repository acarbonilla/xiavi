from django.db import models
from django.conf import settings

class ClassroomSession(models.Model):
    """
    A classroom session where the AI acts as a teacher.
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='classroom_sessions')
    topic = models.ForeignKey('conversations.Topic', on_delete=models.SET_NULL, null=True, related_name='classroom_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'classroom_sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Classroom: {self.user.username} - {self.topic.name if self.topic else 'No Topic'}"

class ClassroomMessage(models.Model):
    """
    Messages in a classroom session.
    """
    ROLE_CHOICES = (
        ('user', 'User'),
        ('ai', 'AI'),
    )

    session = models.ForeignKey(ClassroomSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField()
    correction = models.TextField(blank=True, help_text="Correction for user's mistake if any")
    explanation = models.TextField(blank=True, help_text="Explanation of the correction")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classroom_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.text[:50]}..."
