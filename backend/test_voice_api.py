"""
Quick test script to verify voice configuration API endpoints.
Run this after starting the Django server.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# You'll need to replace this with a valid access token
# Get it by logging in through the frontend or using the login endpoint
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def test_get_voices():
    """Test GET /api/conversations/voices/"""
    print("\n=== Testing GET /api/conversations/voices/ ===")
    response = requests.get(f"{BASE_URL}/conversations/voices/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {len(data.get('voices', []))} voices:")
        for voice in data.get('voices', []):
            print(f"  - {voice['name']} ({voice['id']}): {voice['description']}")
    else:
        print(f"❌ Error: {response.text}")
    return response.status_code == 200

def test_create_session_with_voice():
    """Test creating a conversation session with voice preference"""
    print("\n=== Testing POST /api/conversations/sessions/ with voice ===")
    data = {
        "topic": 1,  # Adjust topic ID as needed
        "voice_preference": "professional"
    }
    response = requests.post(
        f"{BASE_URL}/conversations/sessions/",
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        session = response.json()
        print(f"✅ Success! Created session {session['id']} with voice: {session.get('voice_preference')}")
        return session['id']
    else:
        print(f"❌ Error: {response.text}")
    return None

def test_update_profile_voice():
    """Test updating user profile voice preference"""
    print("\n=== Testing PATCH /api/auth/profile/ ===")
    data = {
        "learner_profile": {
            "preferred_voice": "calm_soothing"
        }
    }
    response = requests.patch(
        f"{BASE_URL}/auth/profile/",
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        profile = response.json()
        preferred_voice = profile.get('learner_profile', {}).get('preferred_voice')
        print(f"✅ Success! Updated profile voice to: {preferred_voice}")
    else:
        print(f"❌ Error: {response.text}")
    return response.status_code == 200

if __name__ == "__main__":
    print("Voice Configuration API Test")
    print("=" * 50)
    print("\n⚠️  Make sure to:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Replace ACCESS_TOKEN with a valid token")
    print("3. Ensure you have at least one topic in the database")
    
    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("\n❌ Please set a valid ACCESS_TOKEN first!")
        print("\nTo get a token:")
        print("1. Login through the frontend")
        print("2. Check localStorage for 'access_token'")
        print("3. Or use: POST /api/auth/login/ with username/password")
    else:
        # Run tests
        test_get_voices()
        test_create_session_with_voice()
        test_update_profile_voice()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
