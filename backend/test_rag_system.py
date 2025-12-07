"""
Test script for RAG document upload and retrieval functionality.
This demonstrates the complete flow: upload PDF/TXT -> ask questions -> get context-aware answers.
"""
import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_FILE = "test_resume.txt"

# You'll need to get a valid token first
# For testing, you can get it from the browser after login or create a test user
USERNAME = "test@test.com"  # Change to your test user
PASSWORD = "test123"  # Change to your test password

def get_auth_token():
    """Get JWT token for authentication."""
    print("1. Getting authentication token...")
    response = requests.post(f"{BASE_URL}/auth/login/", json={
        "email": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()['access']
        print(f"   ✓ Got token: {token[:20]}...")
        return token
    else:
        print(f"   ✗ Error: {response.status_code} - {response.text}")
        print("\n   To test, first create a user or use existing credentials.")
        return None

def create_conversation(token):
    """Create a new conversation session."""
    print("\n2. Creating conversation session...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get first available topic
    topics_response = requests.get(f"{BASE_URL}/conversations/topics/", headers=headers)
    if topics_response.status_code != 200:
        print(f"   ✗ Error getting topics: {topics_response.text}")
        return None
    
    topics = topics_response.json()
    if not topics:
        print("   ✗ No topics available")
        return None
    
    topic_id = topics[0]['id']
    
    # Create session
    response = requests.post(
        f"{BASE_URL}/conversations/sessions/",
        headers=headers,
        json={"topic": topic_id}
    )
    
    if response.status_code == 201:
        session_id = response.json()['id']
        print(f"   ✓ Created session ID: {session_id}")
        return session_id
    else:
        print(f"   ✗ Error: {response.status_code} - {response.text}")
        return None

def upload_document(token, session_id, file_path):
    """Upload a document to the conversation."""
    print(f"\n3. Uploading document: {file_path}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'text/plain')}
        response = requests.post(
            f"{BASE_URL}/conversations/sessions/{session_id}/upload_document/",
            headers=headers,
            files=files
        )
    
    if response.status_code == 201:
        data = response.json()
        print(f"   ✓ Document uploaded successfully!")
        print(f"     - Filename: {data['filename']}")
        print(f"     - Size: {data['file_size_kb']} KB")
        print(f"     - Processed: {data['processed']}")
        print(f"     - Chunks: {data['chunk_count']}")
        return data['id']
    else:
        print(f"   ✗ Error: {response.status_code}")
        print(f"     {response.text}")
        return None

def get_documents(token, session_id):
    """Get all documents for a session."""
    print(f"\n4. Fetching documents for session {session_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/conversations/sessions/{session_id}/documents/",
        headers=headers
    )
    
    if response.status_code == 200:
        docs = response.json()
        print(f"   ✓ Found {len(docs)} document(s)")
        for doc in docs:
            print(f"     - {doc['filename']}: {doc['chunk_count']} chunks")
        return docs
    else:
        print(f"   ✗ Error: {response.status_code} - {response.text}")
        return []

def test_rag_retrieval(token, session_id):
    """
    Test RAG retrieval by directly calling the Gemini service.
    In production, this happens when user speaks.
    """
    print(f"\n5. Testing RAG retrieval with sample questions...")
    
    # Import the services
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    from apps.conversations.models import ConversationSession
    from services.gemini_service import GeminiService
    
    # Get the session
    session = ConversationSession.objects.get(id=session_id)
    gemini = GeminiService()
    
    # Test questions
    questions = [
        "What is the candidate's current job title?",
        "What programming languages does this person know?",
        "Tell me about their work experience at Tech Corp"
    ]
    
    print("\n   Testing questions:")
    for i, question in enumerate(questions, 1):
        print(f"\n   Q{i}: {question}")
        
        response_data = gemini.generate_conversation_response(
            topic="Career Discussion",
            conversation_history=[],
            user_message=question,
            session=session
        )
        
        response_text = response_data.get('response', '')
        referenced_docs = response_data.get('referenced_documents', [])
        
        print(f"   A{i}: {response_text[:200]}...")
        if referenced_docs:
            print(f"   📄 Used documents: {', '.join(referenced_docs)}")
        else:
            print(f"   ℹ️  No documents used (similarity < 0.5)")

def main():
    """Main test flow."""
    print("=" * 60)
    print("RAG DOCUMENT UPLOAD & RETRIEVAL TEST")
    print("=" * 60)
    
    # Check if test file exists
    if not os.path.exists(TEST_FILE):
        print(f"\n✗ Test file not found: {TEST_FILE}")
        print("  Please create a test document first.")
        return
    
    # Step 1: Authenticate
    token = get_auth_token()
    if not token:
        print("\n⚠️  Skipping API tests (no auth). Testing RAG directly...")
        # For testing RAG without API, you can manually create a session in Django admin
        # and update the session_id below
        test_session_id = input("\nEnter existing session ID to test RAG (or press Enter to skip): ").strip()
        if test_session_id:
            try:
                test_rag_retrieval(None, int(test_session_id))
            except Exception as e:
                print(f"✗ Error: {e}")
        return
    
    # Step 2: Create conversation
    session_id = create_conversation(token)
    if not session_id:
        return
    
    # Step 3: Upload document
    doc_id = upload_document(token, session_id, TEST_FILE)
    if not doc_id:
        return
    
    # Step 4: Verify upload
    get_documents(token, session_id)
    
    # Step 5: Test RAG retrieval
    try:
        test_rag_retrieval(token, session_id)
    except Exception as e:
        print(f"\n✗ RAG test error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
    print(f"\nYour conversation session ID: {session_id}")
    print("You can now use this session in the frontend to:")
    print("  1. Upload more documents")
    print("  2. Speak questions about the documents")
    print("  3. Get AI responses with document context")

if __name__ == "__main__":
    main()
