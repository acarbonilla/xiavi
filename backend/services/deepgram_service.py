"""
Deepgram Speech-to-Text Service Integration using REST API directly
"""
import os
import time
import json
import httpx
from django.conf import settings


class DeepgramService:
    """
    Service for transcribing video/audio using Deepgram API via REST.
    """
    
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY is not set in settings")
        self.base_url = "https://api.deepgram.com/v1"
    
    def transcribe_video(self, video_path):
        """
        Transcribe a video file to text using Deepgram REST API.
        
        Args:
            video_path: Path to the video file
        
        Returns:
            dict: {
                'text': str,
                'confidence': float,
                'processing_time': float
            }
        """
        start_time = time.time()
        
        try:
            # Validate file exists and has content
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            file_size = os.path.getsize(video_path)
            if file_size == 0:
                raise ValueError(f"Video file is empty (0 bytes): {video_path}")
            
            print(f"Transcribing file: {video_path} ({file_size} bytes)")
            
            # Read audio file
            with open(video_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Prepare API request
            url = f"{self.base_url}/listen"
            params = {
                "model": "nova-2",
                "smart_format": "true",
                "punctuate": "true",
            }
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/webm",
            }
            
            # Make the API call
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, params=params, headers=headers, content=audio_data)
                response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract transcript
            channels = result.get('results', {}).get('channels', [])
            if not channels or len(channels) == 0:
                raise ValueError("No channels found in Deepgram response")
            
            alternatives = channels[0].get('alternatives', [])
            if not alternatives or len(alternatives) == 0:
                raise ValueError("No alternatives found in Deepgram response")
            
            transcript = alternatives[0].get('transcript', '')
            confidence = alternatives[0].get('confidence', 0.0)
            
            processing_time = time.time() - start_time
            
            return {
                'text': transcript,
                'confidence': confidence,
                'processing_time': processing_time
            }
        
        except FileNotFoundError as e:
            raise Exception(f"File error: {str(e)}")
        except ValueError as e:
            raise Exception(f"Validation error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Deepgram API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            error_msg = f"Deepgram transcription failed: {str(e)}"
            if hasattr(e, '__class__'):
                error_msg += f" (Type: {e.__class__.__name__})"
            raise Exception(error_msg)
    
    def transcribe_audio(self, audio_path):
        """
        Transcribe an audio file to text.
        """
        return self.transcribe_video(audio_path)
