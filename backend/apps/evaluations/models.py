from django.db import models


class Evaluation(models.Model):
    """
    AI-generated evaluation for interview responses.
    """
    interview = models.OneToOneField('interviews.Interview', on_delete=models.CASCADE, related_name='evaluation')
    overall_score = models.FloatField(default=0.0, help_text='Overall score out of 100')
    communication_score = models.FloatField(default=0.0)
    content_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    clarity_score = models.FloatField(default=0.0)
    feedback = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'evaluations'
        verbose_name = 'Evaluation'
        verbose_name_plural = 'Evaluations'
    
    def __str__(self):
        return f"Evaluation: {self.interview} - Score: {self.overall_score}"


class QuestionEvaluation(models.Model):
    """
    Individual question evaluation within an interview.
    """
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='question_evaluations')
    video_response = models.OneToOneField('responses.VideoResponse', on_delete=models.CASCADE, related_name='question_evaluation')
    score = models.FloatField(default=0.0)
    feedback = models.TextField(blank=True)
    key_points = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'question_evaluations'
        verbose_name = 'Question Evaluation'
        verbose_name_plural = 'Question Evaluations'
    
    def __str__(self):
        return f"Q Eval: {self.video_response} - Score: {self.score}"
