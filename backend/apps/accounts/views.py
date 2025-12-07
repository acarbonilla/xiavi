from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    """
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class LoginView(APIView):
    """
    User login endpoint - returns JWT tokens.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_serializer.data
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """
    User logout endpoint - blacklists refresh token.
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Change user password.
    """
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'error': 'Wrong password'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoalStatusView(APIView):
    """
    Get current daily goal progress and status.
    """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        from services.goal_tracker import GoalTracker
        
        try:
            # Ensure user has a learner profile
            if not hasattr(request.user, 'learner_profile'):
                # Create profile if it doesn't exist
                from apps.accounts.models import LearnerProfile
                LearnerProfile.objects.create(user=request.user)
            
            progress = GoalTracker.get_daily_progress(request.user)
            return Response(progress)
        except Exception as e:
            # Return safe defaults if there's an error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Goal status error: {str(e)}")
            
            return Response({
                'conversations_today': 0,
                'speaking_minutes_today': 0.0,
                'goal_conversations': 1,
                'goal_minutes': 10,
                'conversations_progress': 0.0,
                'minutes_progress': 0.0,
                'goals_met': False,
                'current_streak': 0,
                'longest_streak': 0,
            })


class SetGoalsView(APIView):
    """
    Update daily goal settings.
    """
    permission_classes = (IsAuthenticated,)
    
    def patch(self, request):
        profile = request.user.learner_profile
        
        daily_goal_minutes = request.data.get('daily_goal_minutes')
        daily_goal_conversations = request.data.get('daily_goal_conversations')
        
        if daily_goal_minutes is not None:
            if daily_goal_minutes < 1 or daily_goal_minutes > 120:
                return Response(
                    {'error': 'Daily goal minutes must be between 1 and 120'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            profile.daily_goal_minutes = daily_goal_minutes
        
        if daily_goal_conversations is not None:
            if daily_goal_conversations < 1 or daily_goal_conversations > 20:
                return Response(
                    {'error': 'Daily goal conversations must be between 1 and 20'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            profile.daily_goal_conversations = daily_goal_conversations
        
        profile.save()
        
        return Response({
            'daily_goal_minutes': profile.daily_goal_minutes,
            'daily_goal_conversations': profile.daily_goal_conversations
        })


class StreakHistoryView(APIView):
    """
    Get activity history for streak visualization.
    """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        from services.goal_tracker import GoalTracker
        
        days = int(request.query_params.get('days', 30))
        if days > 365:
            days = 365
        
        history = GoalTracker.get_streak_history(request.user, days)
        return Response(history)
