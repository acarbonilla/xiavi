from django.db import models


class TrainingSession(models.Model):
    """
    Practice training sessions for applicants.
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
    )
    
    applicant = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='training_sessions')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'training_sessions'
        verbose_name = 'Training Session'
        verbose_name_plural = 'Training Sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Training: {self.applicant.username} - {self.question.text[:30]}"


class TrainingFeedback(models.Model):
    """
    Instant AI feedback for training sessions.
    """
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='feedbacks')
    video_file = models.FileField(upload_to='training/videos/')
    transcript = models.TextField(blank=True)
    score = models.FloatField(default=0.0)
    feedback = models.TextField(blank=True)
    tips = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'training_feedbacks'
        verbose_name = 'Training Feedback'
        verbose_name_plural = 'Training Feedbacks'
    
    def __str__(self):
        return f"Feedback: {self.session} - Score: {self.score}"
