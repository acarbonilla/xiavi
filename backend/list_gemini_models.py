"""
List available Gemini models
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERROR: GEMINI_API_KEY not set")
    exit(1)

genai.configure(api_key=api_key)

print("\n=== Available Gemini Models ===\n")

try:
    models = genai.list_models()
    
    # Filter models that support generateContent
    content_models = []
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            content_models.append(model)
            print(f"✓ {model.name}")
            print(f"  Display name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Methods: {', '.join(model.supported_generation_methods)}")
            print()
    
    print(f"\nFound {len(content_models)} models supporting generateContent\n")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
