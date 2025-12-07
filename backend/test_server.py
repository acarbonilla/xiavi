"""
Make a simple HTTP request to check if the server is responding
"""
import requests
import json

# Test if server is running
url = "http://localhost:8000/api/"

try:
    response = requests.get(url)
    print(f"Server status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Cannot connect to server: {e}")

# List available endpoints
try:
    response = requests.options(url)
    print(f"\nServer is running on port 8000")
except Exception as e:
    print(f"Error: {e}")
