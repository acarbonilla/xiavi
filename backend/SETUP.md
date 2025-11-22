# Backend Setup Guide

## Quick Start

### 1. Virtual Environment (✅ Done)
```bash
cd backend
python -m venv venv
```

### 2. Activate & Install Dependencies (⏳ In Progress)
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `backend/.env`:
```env
# Database
DB_NAME=xiav_speech_ai
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# API Keys
DEEPGRAM_API_KEY=your_deepgram_api_key
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/google-credentials.json
```

### 4. Database Setup
```bash
# Create PostgreSQL database
createdb xiav_speech_ai

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Create Sample Topics
```bash
python manage.py shell
```

Paste this:
```python
from apps.conversations.models import Topic

topics = [
    {
        "name": "Casual Chat",
        "description": "Everyday conversations about life, hobbies, and interests",
        "difficulty": "beginner",
        "icon": "message-circle",
        "color": "blue"
    },
    {
        "name": "Business Communication",
        "description": "Professional discussions, meetings, and presentations",
        "difficulty": "intermediate",
        "icon": "briefcase",
        "color": "purple"
    },
    {
        "name": "Academic Discussion",
        "description": "Intellectual conversations about science, history, and literature",
        "difficulty": "advanced",
        "icon": "book-open",
        "color": "green"
    },
    {
        "name": "Travel & Culture",
        "description": "Conversations about travel experiences and cultural topics",
        "difficulty": "beginner",
        "icon": "plane",
        "color": "orange"
    },
    {
        "name": "Current Events",
        "description": "Discuss news, trends, and current affairs",
        "difficulty": "intermediate",
        "icon": "newspaper",
        "color": "red"
    },
]

for topic_data in topics:
    Topic.objects.create(**topic_data)

print("✅ Topics created successfully!")
exit()
```

### 7. Run Server
```bash
python manage.py runserver
```

Server will be available at: `http://localhost:8000`

## API Keys Setup

### Deepgram (Speech-to-Text)
1. Sign up at https://deepgram.com
2. Get API key from dashboard
3. Add to `.env` as `DEEPGRAM_API_KEY`

### Google Gemini (AI)
1. Go to https://makersuite.google.com/app/apikey
2. Create API key
3. Add to `.env` as `GEMINI_API_KEY`

### Google Cloud TTS (Text-to-Speech)
1. Create project at https://console.cloud.google.com
2. Enable Text-to-Speech API
3. Create service account
4. Download JSON credentials
5. Add path to `.env` as `GOOGLE_APPLICATION_CREDENTIALS`

## Troubleshooting

### Pillow Installation Error
If you get an error installing Pillow, install it separately:
```bash
pip install Pillow
```

### PostgreSQL Connection Error
Make sure PostgreSQL is running:
```bash
# Windows
net start postgresql-x64-14
```

### Import Errors
Make sure virtual environment is activated:
```bash
.\venv\Scripts\Activate.ps1
```

## Verify Installation
```bash
python manage.py check
```

Should show: `System check identified no issues (0 silenced).`
