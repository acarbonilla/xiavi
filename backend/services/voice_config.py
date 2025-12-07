"""
Voice configuration for Google Cloud Text-to-Speech.
Defines available voice options and their metadata.
"""

# Voice choices for database and API
VOICE_CHOICES = [
    ('light_cheerful', 'Light & Cheerful'),
    ('warm_friendly', 'Warm & Friendly'),
    ('professional', 'Professional'),
    ('calm_soothing', 'Calm & Soothing'),
]

# Mapping of voice choice keys to Google TTS voice names
VOICE_NAME_MAP = {
    'light_cheerful': 'en-US-Neural2-C',
    'warm_friendly': 'en-US-Neural2-F',
    'professional': 'en-US-Neural2-A',
    'calm_soothing': 'en-US-Neural2-H',
}

# Detailed metadata for each voice option
VOICE_METADATA = {
    'light_cheerful': {
        'id': 'light_cheerful',
        'name': 'Light & Cheerful',
        'description': 'Energetic and upbeat tone, perfect for casual conversations',
        'google_voice': 'en-US-Neural2-C',
        'gender': 'female',
        'tone': 'energetic',
        'pitch_range': 'higher',
    },
    'warm_friendly': {
        'id': 'warm_friendly',
        'name': 'Warm & Friendly',
        'description': 'Conversational and approachable, great for everyday learning',
        'google_voice': 'en-US-Neural2-F',
        'gender': 'female',
        'tone': 'conversational',
        'pitch_range': 'medium',
    },
    'professional': {
        'id': 'professional',
        'name': 'Professional',
        'description': 'Clear and authoritative, ideal for business communication practice',
        'google_voice': 'en-US-Neural2-A',
        'gender': 'male',
        'tone': 'authoritative',
        'pitch_range': 'medium-low',
    },
    'calm_soothing': {
        'id': 'calm_soothing',
        'name': 'Calm & Soothing',
        'description': 'Gentle and reassuring, perfect for relaxed learning sessions',
        'google_voice': 'en-US-Neural2-H',
        'gender': 'female',
        'tone': 'gentle',
        'pitch_range': 'medium',
    },
}

# Default voice
DEFAULT_VOICE = 'warm_friendly'


def get_voice_name(choice_key):
    """
    Get Google TTS voice name from choice key.
    
    Args:
        choice_key: Voice choice key (e.g., 'light_cheerful')
    
    Returns:
        str: Google TTS voice name (e.g., 'en-US-Neural2-C')
    """
    return VOICE_NAME_MAP.get(choice_key, VOICE_NAME_MAP[DEFAULT_VOICE])


def get_voice_metadata(choice_key):
    """
    Get detailed metadata for a voice choice.
    
    Args:
        choice_key: Voice choice key
    
    Returns:
        dict: Voice metadata or None if not found
    """
    return VOICE_METADATA.get(choice_key)


def get_all_voices():
    """
    Get all available voice options with metadata.
    
    Returns:
        list: List of voice metadata dictionaries
    """
    return [VOICE_METADATA[key] for key, _ in VOICE_CHOICES]
