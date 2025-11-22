"""
Google Text-to-Speech Service Integration
"""
import os
from google.cloud import texttospeech
from django.conf import settings
from django.core.files.base import ContentFile


class GoogleTTSService:
    """
    Service for generating speech from text using Google Cloud TTS.
    """
    
    def __init__(self):
        # Set credentials from settings
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        self.client = texttospeech.TextToSpeechClient()
    
    def generate_speech(self, text, output_path=None, language_code='en-US', voice_name='en-US-Neural2-F'):
        """
        Generate speech audio from text.
        
        Args:
            text: Text to convert to speech
            output_path: Optional path to save the audio file
            language_code: Language code (default: en-US)
            voice_name: Voice name (default: en-US-Neural2-F - female voice)
        
        Returns:
            bytes: Audio content
        """
        try:
            # Set the text input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name
            )
            
            # Select the audio file type
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0
            )
            
            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save to file if output path provided
            if output_path:
                with open(output_path, 'wb') as out:
                    out.write(response.audio_content)
            
            return response.audio_content
        
        except Exception as e:
            raise Exception(f"Google TTS generation failed: {str(e)}")
    
    def generate_question_audio(self, question_text):
        """
        Generate audio for a question.
        
        Args:
            question_text: The question text
        
        Returns:
            ContentFile: Django file object with audio content
        """
        audio_content = self.generate_speech(question_text)
        return ContentFile(audio_content, name='question_audio.mp3')
