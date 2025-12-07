"""
Service for tracking daily goals and user progress.
"""
from datetime import date, timedelta
from django.utils import timezone
from apps.accounts.models import LearnerProfile
from apps.conversations.models import ConversationSession


class GoalTracker:
    """Service for managing daily goals and streaks."""
    
    @staticmethod
    def get_daily_progress(user):
        """
        Calculate user's progress toward daily goals.
        
        Returns:
            dict: Progress information including:
                - conversations_today: int
                - speaking_minutes_today: float
                - goal_conversations: int
                - goal_minutes: int
                - conversations_progress: float (0-100)
                - minutes_progress: float (0-100)
                - goals_met: bool
        """
        profile = user.learner_profile
        today = timezone.now().date()
        
        # Get today's conversations
        today_sessions = ConversationSession.objects.filter(
            user=user,
            started_at__date=today,
            status='completed'
        )
        
        conversations_today = today_sessions.count()
        speaking_seconds_today = sum(s.total_speaking_time for s in today_sessions)
        speaking_minutes_today = speaking_seconds_today / 60.0
        
        # Calculate progress percentages
        conversations_progress = min(100, (conversations_today / profile.daily_goal_conversations) * 100) if profile.daily_goal_conversations > 0 else 0
        minutes_progress = min(100, (speaking_minutes_today / profile.daily_goal_minutes) * 100) if profile.daily_goal_minutes > 0 else 0
        
        # Both goals must be met
        goals_met = conversations_today >= profile.daily_goal_conversations and speaking_minutes_today >= profile.daily_goal_minutes
        
        return {
            'conversations_today': conversations_today,
            'speaking_minutes_today': round(speaking_minutes_today, 1),
            'goal_conversations': profile.daily_goal_conversations,
            'goal_minutes': profile.daily_goal_minutes,
            'conversations_progress': round(conversations_progress, 1),
            'minutes_progress': round(minutes_progress, 1),
            'goals_met': goals_met,
            'current_streak': profile.current_streak,
            'longest_streak': profile.longest_streak,
        }
    
    @staticmethod
    def check_and_update_streak(user, conversation_date=None):
        """
        Check and update user's streak based on conversation completion.
        
        Args:
            user: User object
            conversation_date: Date of conversation (defaults to today)
        """
        if conversation_date is None:
            conversation_date = timezone.now().date()
        
        profile = user.learner_profile
        
        # If first conversation ever
        if profile.last_conversation_date is None:
            profile.current_streak = 1
            profile.longest_streak = 1
            profile.last_conversation_date = conversation_date
            profile.save()
            return
        
        # Calculate days since last conversation
        days_diff = (conversation_date - profile.last_conversation_date).days
        
        if days_diff == 0:
            # Same day, no streak change (already counted)
            return
        elif days_diff == 1:
            # Consecutive day, increment streak
            profile.current_streak += 1
            if profile.current_streak > profile.longest_streak:
                profile.longest_streak = profile.current_streak
        elif days_diff > 1:
            # Streak broken, reset to 1
            profile.current_streak = 1
        
        profile.last_conversation_date = conversation_date
        profile.save()
    
    @staticmethod
    def get_streak_history(user, days=30):
        """
        Get conversation activity for the last N days.
        
        Returns:
            list: List of dicts with {date, conversation_count}
        """
        today = timezone.now().date()
        start_date = today - timedelta(days=days-1)
        
        # Get all conversations in range
        sessions = ConversationSession.objects.filter(
            user=user,
            started_at__date__gte=start_date,
            started_at__date__lte=today,
            status='completed'
        ).values('started_at__date').annotate(
            count=models.Count('id')
        )
        
        # Create a dict for quick lookup
        activity_dict = {s['started_at__date']: s['count'] for s in sessions}
        
        # Build complete history
        history = []
        current_date = start_date
        while current_date <= today:
            history.append({
                'date': current_date.isoformat(),
                'conversation_count': activity_dict.get(current_date, 0)
            })
            current_date += timedelta(days=1)
        
        return history


# Import for annotation
from django.db import models
