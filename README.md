# XiAv Speech AI - Conversational Learning Platform

An AI-powered platform for improving speech communication skills through natural conversations.

## 🚀 Features

- **AI Conversations**: Have natural conversations with AI on any topic
- **Speech-to-Text**: Automatic transcription using Deepgram
- **Text-to-Speech**: AI responses with Google TTS
- **Smart Feedback**: Detailed analysis of your communication skills
- **Progress Tracking**: Monitor your improvement over time
- **Multiple Topics**: Practice casual chat, business, academic discussions, and more

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **AI Services**:
  - Deepgram (Speech-to-Text)
  - Google Cloud TTS (Text-to-Speech)
  - Google Gemini 2.5 Flash (Conversational AI & Analysis)

### Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Node.js 18+
- API Keys:
  - Deepgram API Key
  - Google Cloud Service Account (for TTS)
  - Google Gemini API Key

## 🔧 Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `backend/.env` with your credentials:
```env
SECRET_KEY=your-secret-key
DB_NAME=xiav_speech_ai
DB_USER=postgres
DB_PASSWORD=your-password
DEEPGRAM_API_KEY=your-deepgram-key
GEMINI_API_KEY=your-gemini-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### 3. Database Setup
```bash
createdb xiav_speech_ai
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Create Sample Topics
```bash
python manage.py shell
```
```python
from apps.conversations.models import Topic

topics = [
    {"name": "Casual Chat", "description": "Everyday conversations about life, hobbies, and interests", "difficulty": "beginner", "icon": "message-circle", "color": "blue"},
    {"name": "Business Communication", "description": "Professional discussions, meetings, and presentations", "difficulty": "intermediate", "icon": "briefcase", "color": "purple"},
    {"name": "Academic Discussion", "description": "Intellectual conversations about science, history, and literature", "difficulty": "advanced", "icon": "book-open", "color": "green"},
    {"name": "Travel & Culture", "description": "Conversations about travel experiences and cultural topics", "difficulty": "beginner", "icon": "plane", "color": "orange"},
    {"name": "Current Events", "description": "Discuss news, trends, and current affairs", "difficulty": "intermediate", "icon": "newspaper", "color": "red"},
]

for topic_data in topics:
    Topic.objects.create(**topic_data)
```

### 6. Run Server
```bash
python manage.py runserver
```

API available at: `http://localhost:8000`

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (returns JWT)
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/profile/` - Get user profile

### Conversations
- `GET /api/conversations/topics/` - List available topics
- `GET /api/conversations/sessions/` - List user's conversations
- `POST /api/conversations/sessions/` - Start new conversation
- `GET /api/conversations/sessions/{id}/` - Get conversation details
- `GET /api/conversations/sessions/{id}/messages/` - Get messages
- `POST /api/conversations/sessions/{id}/speak/` - Send audio message
- `POST /api/conversations/sessions/{id}/end/` - End conversation
- `GET /api/conversations/sessions/{id}/feedback/` - Get feedback

## 🎯 How It Works

1. **Choose Topic**: Select a conversation topic
2. **Start Conversation**: AI sends opening message
3. **Speak**: Record your audio response
4. **AI Responds**: 
   - Your audio is transcribed (Deepgram)
   - AI generates response (Gemini)
   - Response is converted to speech (Google TTS)
5. **Continue**: Keep the conversation flowing
6. **Get Feedback**: End conversation and receive detailed analysis

## 🏗️ Project Structure

```
backend/
├── apps/
│   ├── accounts/          # User management & profiles
│   ├── conversations/     # Conversation sessions & messages
│   └── core/              # Shared utilities
├── services/
│   ├── deepgram_service.py    # STT integration
│   ├── google_tts_service.py  # TTS integration
│   └── gemini_service.py      # Conversational AI
└── config/
    ├── settings/
    ├── urls.py
    └── wsgi.py
```

## 📊 Database Models

- **User**: Language level, native/target language
- **LearnerProfile**: Progress tracking (conversations, speaking time, streaks, skill scores)
- **Topic**: Conversation topics with difficulty levels
- **ConversationSession**: Individual conversation sessions
- **ConversationMessage**: User and AI messages
- **ConversationFeedback**: AI-generated feedback and scores

## 🎓 Feedback Metrics

The AI analyzes your speech on 6 dimensions:
- **Clarity**: Pronunciation and understandability
- **Fluency**: Speaking smoothness and pace
- **Vocabulary**: Word choice and richness
- **Grammar**: Grammatical accuracy
- **Confidence**: Speaking confidence
- **Engagement**: Conversation participation

## 📝 License

MIT License
