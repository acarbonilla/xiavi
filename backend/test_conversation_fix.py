from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.conversations.models import Topic, ConversationSession

User = get_user_model()

def test_conversation_flow():
    print("Setting up test data...")
    # Create user
    user, created = User.objects.get_or_create(username='testuser_fix', email='test_fix@example.com')
    if created:
        user.set_password('password123')
        user.save()
        # Create profile
        from apps.accounts.models import LearnerProfile
        LearnerProfile.objects.get_or_create(user=user)
    
    # Create topic
    topic, _ = Topic.objects.get_or_create(name='Test Topic Fix', description='Test Description Fix')
    
    client = APIClient()
    client.force_authenticate(user=user)
    
    print("\nTesting start_conversation...")
    response = client.post('/api/conversations/sessions/start_conversation/', {'topic_id': topic.id}, format='json')
    
    if response.status_code == 201:
        print("SUCCESS: start_conversation returned 201 Created")
        session_id = response.data['id']
        print(f"Session ID: {session_id}")
        
        # Add a user message to ensure feedback generation is triggered
        from apps.conversations.models import ConversationMessage
        session = ConversationSession.objects.get(id=session_id)
        ConversationMessage.objects.create(
            session=session,
            role='user',
            text="Hello, this is a test message.",
            duration=5
        )
        print("Added test user message")
    else:
        print(f"FAILED: start_conversation returned {response.status_code}")
        print(response.data)
        return
    
    print("\nTesting end_conversation (First Call)...")
    # This should succeed and create feedback (or fallback)
    response = client.post(f'/api/conversations/sessions/{session_id}/end/')
    
    if response.status_code == 200:
        print("SUCCESS: end_conversation (1st) returned 200 OK")
        print(response.data)
    else:
        print(f"FAILED: end_conversation (1st) returned {response.status_code}")
        print(response.data)
        
    print("\nTesting end_conversation (Second Call - Idempotency)...")
    # This should ALSO succeed (200 OK) now, instead of 400
    response = client.post(f'/api/conversations/sessions/{session_id}/end/')
    
    if response.status_code == 200:
        print("SUCCESS: end_conversation (2nd) returned 200 OK (Idempotency works)")
        print(response.data)
    else:
        print(f"FAILED: end_conversation (2nd) returned {response.status_code}")
        print(response.data)

    print("\nTesting feedback existence...")
    # Check if feedback exists (either real or fallback)
    response = client.get(f'/api/conversations/sessions/{session_id}/feedback/')
    if response.status_code == 200:
        print("SUCCESS: Feedback exists")
        print(f"Score: {response.data.get('overall_score')}")
        print(f"Text: {response.data.get('feedback_text')}")
    else:
        print(f"FAILED: Feedback not found (404)")
