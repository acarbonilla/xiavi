"""
Deepgram Speech-to-Text Service Integration
"""
import os
import time
import json
from deepgram import DeepgramClient
from django.conf import settings


class DeepgramService:
    """
    Service for transcribing video/audio using Deepgram API.
    """
    
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY is not set in settings")
        self.client = DeepgramClient(api_key=self.api_key)
    
    def transcribe_video(self, video_path):
        """
        Transcribe a video file to text.
        
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
            
            with open(video_path, 'rb') as video_file:
                source = {'buffer': video_file, 'mimetype': 'video/webm'}
                
                options = {
                    "model": "nova-2",
                    "smart_format": True,
                    "punctuate": True,
                    "paragraphs": True,
                }
                
                response = self.client.listen.prerecorded.v('1').transcribe_file(
                    source,
                    options
                )
                
                # Convert response object to dictionary
                response_dict = json.loads(response.to_json())
                
                # Extract transcript
                channels = response_dict.get('results', {}).get('channels', [])
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
        except KeyError as e:
            raise Exception(f"Failed to parse Deepgram response: {str(e)}")
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
