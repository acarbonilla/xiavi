"""
Test the full speak endpoint flow to identify where errors occur
"""
import os
import sys
import django
import tempfile
from io import BytesIO

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from services.deepgram_service import DeepgramService
from services.gemini_service import GeminiService
from services.google_tts_service import GoogleTTSService

print("\n" + "="*60)
print("TESTING FULL SPEAK ENDPOINT FLOW")
print("="*60 + "\n")

# Step 1: Test Deepgram Service
print("Step 1: Testing Deepgram Service...")
try:
    deepgram = DeepgramService()
    print("   ✓ Deepgram service initialized")
    
    # Create a test audio file (empty for now, just to test the flow)
    # In real scenario, we'd need actual audio
    print("   ⚠ Skipping actual transcription test (needs real audio file)")
    
except Exception as e:
    print(f"   ✗ Deepgram initialization failed: {e}")
    import traceback
    traceback.print_exc()

# Step 2: Test Gemini Service
print("\nStep 2: Testing Gemini Service...")
try:
    gemini = GeminiService()
    print("   ✓ Gemini service initialized")
    
    # Test conversation response
    response = gemini.generate_conversation_response(
        topic="Test",
        conversation_history=[],
        user_message="Hello, this is a test"
    )
    print(f"   ✓ Generated response: {response[:60]}...")
    
except Exception as e:
    print(f"   ✗ Gemini service failed: {e}")
    import traceback
    traceback.print_exc()

# Step 3: Test Google TTS Service
print("\nStep 3: Testing Google TTS Service...")
try:
    tts = GoogleTTSService()
    print("   ✓ TTS service initialized")
    
    # Test speech generation
    audio = tts.generate_speech("Hello, this is a test")
    print(f"   ✓ Generated audio: {len(audio)} bytes")
    
except Exception as e:
    print(f"   ✗ TTS service failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print("\nAll services tested. Check results above.")
print("\n")
