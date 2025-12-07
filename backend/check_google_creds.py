"""
Check Google credentials file
"""
import os
from dotenv import load_dotenv

load_dotenv()

path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
print(f"GOOGLE_APPLICATION_CREDENTIALS: {path}")

if path:
    exists = os.path.exists(path)
    print(f"File exists: {exists}")
    if not exists:
        print(f"\n⚠ WARNING: Credentials file not found at: {path}")
else:
    print("⚠ WARNING: GOOGLE_APPLICATION_CREDENTIALS not set in .env")
