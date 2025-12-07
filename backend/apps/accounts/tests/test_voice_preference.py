from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import LearnerProfile
from apps.accounts.serializers import UserSerializer

User = get_user_model()

class VoicePreferenceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.profile = LearnerProfile.objects.create(user=self.user)

    def test_update_voice_preference(self):
        """Test that updating user profile with nested learner_profile updates voice preference."""
        data = {
            'first_name': 'Updated',
            'learner_profile': {
                'preferred_voice': 'professional'
            }
        }
        
        serializer = UserSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        
        # Refresh from db
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.learner_profile.preferred_voice, 'professional')

    def test_update_without_profile_data(self):
        """Test that updating user without profile data doesn't affect profile."""
        original_voice = self.user.learner_profile.preferred_voice
        
        data = {
            'first_name': 'Updated Again'
        }
        
        serializer = UserSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated Again')
        self.assertEqual(user.learner_profile.preferred_voice, original_voice)
