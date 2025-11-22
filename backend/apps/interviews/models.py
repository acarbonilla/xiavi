from django.db import models
from apps.questions.models import Question


class Interview(models.Model):
    """
    Interview session model.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('evaluated', 'Evaluated'),
    )
    
    POSITION_TYPE_CHOICES = (
        ('software_engineer', 'Software Engineer'),
        ('data_scientist', 'Data Scientist'),
        ('product_manager', 'Product Manager'),
        ('designer', 'Designer'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('general', 'General'),
    )
    
    applicant = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='interviews')
    position_type = models.CharField(max_length=50, choices=POSITION_TYPE_CHOICES)
    position_title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'interviews'
        verbose_name = 'Interview'
        verbose_name_plural = 'Interviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.applicant.username} - {self.position_title} ({self.status})"


class InterviewQuestion(models.Model):
    """
    Links interviews to questions with ordering.
    """
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='interview_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'interview_questions'
        verbose_name = 'Interview Question'
        verbose_name_plural = 'Interview Questions'
        ordering = ['order']
        unique_together = ['interview', 'question']
    
    def __str__(self):
        return f"{self.interview} - Q{self.order}"
