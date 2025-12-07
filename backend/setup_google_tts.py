"""
Google TTS Setup Helper

This script helps you set up Google Text-To-Speech for the XiAv Speech AI project.
"""

import os
from pathlib import Path

print("\n" + "="*70)
print("GOOGLE TEXT-TO-SPEECH SETUP HELPER")
print("="*70 + "\n")

backend_dir = Path(__file__).parent
creds_file = backend_dir / "google-tts-key.json"

print(f"Looking for credentials file at: {creds_file}\n")

if creds_file.exists():
    print("✓ Google TTS credentials file found!")
    print(f"  File size: {creds_file.stat().st_size} bytes\n")
else:
    print("✗ Google TTS credentials file NOT found\n")
    print("To set up Google Text-to-Speech:")
    print("\n1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/\n")
    print("2. Enable the Cloud Text-to-Speech API\n")
    print("3. Create a Service Account:")
    print("   - Go to 'IAM & Admin' > 'Service Accounts'")
    print("   - Click 'Create Service Account'")
    print("   - Name it something like 'xiav-tts-service'")
    print("   - Grant it the 'Cloud Text-to-Speech User' role")
    print("   - Click 'Create Key' and choose 'JSON'")
    print("   - Download the JSON key file\n")
    print(f"4. Save the downloaded JSON file as:")
    print(f"   {creds_file}\n")
    print("5. Make sure your .env file has:")
    print(f"   GOOGLE_APPLICATION_CREDENTIALS={creds_file}")
    print("\n" + "="*70)
    print("\nALTERNATIVE: For development/testing without Google TTS:")
    print("The system will work without TTS - AI responses just won't have audio.")
    print("="*70 + "\n")
