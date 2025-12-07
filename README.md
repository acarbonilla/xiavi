# XiAv Speech AI - Conversational Learning Platform

An AI-powered platform for improving English communication skills through natural, engaging conversations with advanced voice activity detection and document-aware AI responses.

## ✨ Latest Updates (November 2025)

- 🎙️ **Smart Voice Detection**: Auto-stop recording with 15% silence threshold and visual countdown
- 🤖 **Enhanced AI Engagement**: Slower-paced, more natural conversations with active listening
- 📄 **RAG Document Upload**: Upload PDFs/TXT files for context-aware conversations
- 🎯 **Improved Prompts**: Better pacing (max 1 question per response), warmer tone

## 🚀 Core Features

### Conversation Features

- **AI Conversations**: Natural dialogue with Google Gemini 2.0 Flash AI
- **Voice Activity Detection (VAD)**: Automatic pause detection (configurable 1-8 seconds)
- **Document-Aware AI (RAG)**: Upload up to 5 documents per session for informed conversations
- **Real-time Audio Visualization**: See your voice levels while speaking
- **Real-time Grammar Corrections**: AI acts as an ESL teacher, providing immediate feedback during conversation

### Technical Capabilities

- **Speech-to-Text**: Real-time transcription via Deepgram
- **Text-to-Speech**: Natural AI voice responses via Google Cloud TTS
- **Progress Tracking**: Monitor improvement over time with streaks and scores
- **Multiple Topics**: 5 conversation topics across 3 difficulty levels

## 🛠️ Tech Stack

### Backend

- **Framework**: Django 5.0.1 + Django REST Framework 3.14.0
- **Database**: PostgreSQL 14+
- **Authentication**: JWT (djangorestframework-simplejwt)
- **AI Services**:
  - **Deepgram SDK 5.3.0** - Speech-to-Text with streaming
  - **Google Cloud TTS 2.33.0** - Text-to-Speech synthesis
  - **Google Gemini 2.0 Flash** - Conversational AI with RAG support
  - **Gemini Text Embedding 004** - 768-dim vector embeddings for RAG
- **Document Processing**:
  - PyPDF2 3.0.1 + pdfplumber 0.11.8 - PDF text extraction
  - charset-normalizer 3.4.0 - Text encoding detection
  - numpy 1.26.4 - Vector similarity calculations

### Frontend

- **Framework**: Next.js 15.5.6 with React Compiler
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Audio**: Web Audio API for real-time audio analysis

## 📋 Prerequisites

- Python 3.13+ (backend uses Python 3.13)
- PostgreSQL 14+
- Node.js 18+
- **API Keys Required**:
  - Deepgram API Key ([Get here](https://deepgram.com))
  - Google Cloud Service Account with TTS API enabled
  - Google Gemini API Key ([Get here](https://ai.google.dev))

## 🔧 Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**

```
Django==5.0.1
djangorestframework==3.14.0
google-generativeai==0.8.5
deepgram-sdk==5.3.0
google-cloud-texttospeech==2.33.0
numpy==1.26.4
PyPDF2==3.0.1
pdfplumber==0.11.8
charset-normalizer==3.4.0
```

### 3. Configure Environment

Create `backend/.env`:

```env
# Django
SECRET_KEY=your-django-secret-key
DEBUG=True

# Database
DB_NAME=xiav_speech_ai
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# API Keys
DEEPGRAM_API_KEY=your-deepgram-api-key
GEMINI_API_KEY=your-gemini-api-key

# Google Cloud TTS
# Place service account JSON in backend/google-tts-key.json
GOOGLE_APPLICATION_CREDENTIALS=google-tts-key.json

# CORS (for local development)
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 4. Database Setup

```bash
# Create database
createdb xiav_speech_ai

# Run migrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser
```

### 5. Load Initial Topics

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
    Topic.objects.get_or_create(name=topic_data["name"], defaults=topic_data)
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Backend available at: `http://localhost:8000`

## 🎨 Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Frontend available at: `http://localhost:3000`

## 📚 API Endpoints

### Authentication

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (returns JWT access + refresh tokens)
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile with learner stats

### Conversations

- `GET /api/conversations/topics/` - List available topics
- `GET /api/conversations/sessions/` - List user's conversation sessions
- `POST /api/conversations/sessions/` - Start new conversation
- `GET /api/conversations/sessions/{id}/` - Get conversation details
- `GET /api/conversations/sessions/{id}/messages/` - Get conversation messages
- `POST /api/conversations/sessions/{id}/speak/` - Send audio message
- `POST /api/conversations/sessions/{id}/end/` - End conversation

### Document Upload (RAG)

- `GET /api/conversations/sessions/{id}/documents/` - List uploaded documents
- `POST /api/conversations/sessions/{id}/documents/upload/` - Upload PDF/TXT
- `DELETE /api/conversations/sessions/{id}/documents/{doc_id}/` - Delete document

**Document Limits:**

- Max 5 documents per session
- Max 10MB per file
- Supported: PDF, TXT
- Documents are session-specific (not global)

## 🎯 How It Works

### Standard Conversation Flow

1. **Choose Topic**: Select from 5 topics (3 difficulty levels)
2. **AI Opens**: Receives warm, welcoming opening message
3. **Voice Recording**:
   - Manual: Click mic, speak, click stop
   - Auto (VAD): Click mic, speak, AI detects silence and auto-sends
4. **Processing**:
   - Audio → Deepgram STT → Text transcript
   - AI generates engaging response (max 1 question)
   - Response → Google TTS → Audio playback
5. **Continue Conversation**: Natural back-and-forth dialogue
6. **End & Analyze**: Get detailed 6-metric feedback

### RAG-Enhanced Conversations

1. **Upload Documents**: Add PDFs/TXT files to session (up to 5)
2. **Processing**: Documents are chunked and embedded (Gemini embeddings)
3. **Contextual Responses**: AI retrieves relevant chunks (cosine similarity)
4. **Smart Answers**: AI provides informed responses based on your documents
5. **Source Attribution**: See which documents were referenced

### Voice Activity Detection

- **15% Silence Threshold**: Detects when you stop speaking
- **Visual Countdown**: Shows remaining time before auto-send
- **Configurable Duration**: Adjust from 1-8 seconds in settings
- **Audio Level Meter**: Real-time visualization of voice input

## 🏗️ Project Structure

```
XiAvSpeechAI/
├── backend/
│   ├── apps/
│   │   ├── accounts/              # User management & profiles
│   │   ├── conversations/         # Sessions, messages, topics
│   │   └── core/                  # Shared utilities
│   ├── services/
│   │   ├── deepgram_service.py    # Speech-to-Text
│   │   ├── google_tts_service.py  # Text-to-Speech
│   │   ├── gemini_service.py      # Conversational AI + RAG
│   │   └── document_service.py    # Document processing & embeddings
│   ├── media/                     # Uploaded audio & documents
│   ├── config/                    # Django settings
│   └── requirements.txt
│
└── frontend/
    ├── app/                       # Next.js pages (App Router)
    │   ├── dashboard/            # Main dashboard
    │   ├── conversation/[id]/    # Conversation interface
    │   ├── history/              # Past conversations
    │   └── progress/             # Progress tracking
    ├── components/
    │   ├── DocumentUpload.tsx    # RAG document upload
    │   └── ...
    ├── lib/
    │   └── api.ts               # API client
    └── types/                   # TypeScript definitions
```

## 📊 Database Models

### Core Models

- **User**: Authentication + language preferences
- **LearnerProfile**: Progress tracking (conversations, speaking time, streaks, skill scores, topics covered)
- **Topic**: Conversation topics with difficulty levels (beginner/intermediate/advanced)
- **ConversationSession**: Individual conversation instances
- **ConversationMessage**: User and AI messages with audio/transcripts
- **ConversationFeedback**: AI-generated analysis with 6-dimension scores

### RAG Models

- **DocumentUpload**: Uploaded PDF/TXT files (max 5 per session)
- **DocumentChunk**: Text chunks with 768-dim embeddings for similarity search

## 🎓 AI Feedback Metrics

The AI analyzes conversations across 6 dimensions (0-100):

| Metric         | Description                              |
| -------------- | ---------------------------------------- |
| **Clarity**    | Pronunciation and understandability      |
| **Fluency**    | Speaking smoothness and natural pace     |
| **Vocabulary** | Word choice richness and appropriateness |
| **Grammar**    | Grammatical accuracy                     |
| **Confidence** | Speaking confidence and assertiveness    |
| **Engagement** | Active participation in conversation     |

**Overall Score**: Average of all 6 metrics

## 🧪 Testing

### Backend Tests

```bash
cd backend
python manage.py test
```

### Frontend Build

```bash
cd frontend
npm run build
```

## 🔍 Troubleshooting

### Common Issues

**1. `ModuleNotFoundError: No module named 'numpy'`**

```bash
# Ensure you're in the virtual environment
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

**2. Webpack Error on Frontend Refresh**

```powershell
# Clear Next.js cache
cd frontend
Remove-Item -Recurse -Force .next
npm run dev
```

**3. Google TTS Authentication Error**

- Ensure `google-tts-key.json` exists in `backend/`
- Verify service account has "Cloud Text-to-Speech API User" role
- Check `GOOGLE_APPLICATION_CREDENTIALS` in `.env`

**4. Deepgram Connection Issues**

- Verify API key in `.env`
- Check network/firewall settings
- Ensure sufficient API credits

## 📝 Development Notes

### Recent Enhancements (Nov 2025)

1. **AI Engagement Improvements**:

   - Enhanced prompts for slower pacing
   - Active listening before questioning
   - Max 1 question per response
   - Warmer, more encouraging tone

2. **Voice Activity Detection**:

   - 15% audio level threshold
   - Visual countdown indicator
   - Configurable pause duration (1-8s)

3. **RAG Implementation**:
   - Document chunking with overlap
   - Gemini text-embedding-004 (768-dim)
   - Cosine similarity search (threshold: 0.35)
   - Source attribution in responses

### Configuration Options

**Voice Detection Settings** (Frontend):

- `SILENCE_THRESHOLD`: 15% audio level
- `silenceDuration`: Default 4000ms (4 seconds)
- Adjustable range: 1000-8000ms

**Document Processing** (Backend):

- `CHUNK_SIZE`: 800 tokens (~3200 chars)
- `CHUNK_OVERLAP`: 100 tokens (~400 chars)
- `MAX_DOCUMENTS_PER_SESSION`: 5
- `MAX_FILE_SIZE`: 10MB

## 📄 License

MIT License

## 🤝 Contributing

This is an educational project. Contributions welcome!

## 📞 Support

For issues or questions, please check:

1. This README
2. Backend setup guide: `backend/SETUP.md`
3. Frontend documentation
4. API documentation: `http://localhost:8000/api/`

---

**Built with ❤️ for English language learners**
