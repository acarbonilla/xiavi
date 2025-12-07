"""
Quick script to check if environment variables are loaded
"""
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("\n=== Environment Variables Check ===\n")

# Check each required variable
required_vars = {
    'DEEPGRAM_API_KEY': os.getenv('DEEPGRAM_API_KEY'),
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
    'GOOGLE_APPLICATION_CREDENTIALS': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
}

for var_name, var_value in required_vars.items():
    if var_value and var_value.strip():
        # Show first 10 chars and last 4 chars for security
        if len(var_value) > 14:
            masked_value = f"{var_value[:10]}...{var_value[-4:]}"
        else:
            masked_value = f"{var_value[:3]}..." if len(var_value) > 3 else "***"
        print(f"✓ {var_name}: {masked_value} (length: {len(var_value)})")
    else:
        print(f"✗ {var_name}: NOT SET or EMPTY")

print("\n" + "="*40 + "\n")
