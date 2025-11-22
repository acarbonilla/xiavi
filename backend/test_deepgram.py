import os
import inspect
from dotenv import load_dotenv
from pathlib import Path
from deepgram import DeepgramClient

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

api_key = os.getenv('DEEPGRAM_API_KEY')
print(f"API Key found: {bool(api_key)}")

if api_key:
    try:
        deepgram = DeepgramClient(api_key=api_key)
        
        url = "https://static.deepgram.com/examples/interview_speech-analytics.wav"
        source = {"url": url}
        options = {
            "model": "nova-2",
            "smart_format": True,
        }
        
        print("Calling transcribe_url with url kwarg...")
        response = deepgram.listen.v1.media.transcribe_url(url=source["url"], **options)
        print("SUCCESS!")
        print(response)
    except Exception as e:
        print(f"FAILED: {e}")
