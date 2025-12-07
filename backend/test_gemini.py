"""
Test Gemini service to verify it's working
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from services.gemini_service import GeminiService

print("\n=== Testing Gemini Service ===\n")

try:
    # Initialize service
    print("1. Initializing Gemini service...")
    gemini_service = GeminiService()
    print("   ✓ Service initialized successfully")
    
    # Test conversation response
    print("\n2. Testing conversation response generation...")
    response = gemini_service.generate_conversation_response(
        topic="Hobbies",
        conversation_history=[],
        user_message="I like playing guitar"
    )
    print(f"   ✓ Response generated: {response[:80]}...")
    
    print("\n3. Testing opening message generation...")
    opening = gemini_service.generate_opening_message("Travel")
    print(f"   ✓ Opening message: {opening[:80]}...")
    
    print("\n" + "="*50)
    print("✓ All tests passed! Gemini service is working.")
    print("="*50 + "\n")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n")
