"""
Test Deepgram with a real audio file
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

import django
django.setup()

from services.deepgram_service import DeepgramService

# Create a simple test audio file (silence)
import wave
import struct

test_file = 'test_audio.wav'

# Create a 1-second silent WAV file
with wave.open(test_file, 'w') as wav_file:
    wav_file.setnchannels(1)  # mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(16000)  # 16kHz
    # Write 1 second of silence
    for _ in range(16000):
        wav_file.writeframes(struct.pack('h', 0))

print("Testing Deepgram transcription...")

try:
    service = DeepgramService()
    result = service.transcribe_video(test_file)
    print(f"✓ Transcription successful!")
    print(f"  Text: '{result['text']}'")
    print(f"  Confidence: {result['confidence']}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
