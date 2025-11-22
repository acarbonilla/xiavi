"""
Google Gemini AI Service Integration for Conversational Learning
"""
import google.generativeai as genai
from django.conf import settings
import json


class GeminiService:
    """
    Service for conversational AI and speech analysis using Google Gemini.
    """
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings")
        
        genai.configure(api_key=self.api_key)
        # Use a reliable model that doesn't hit quota limits easily
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')
    
    def generate_conversation_response(self, topic, conversation_history, user_message):
        """
        Generate natural conversation response based on context.
        
        Args:
            topic: Conversation topic
            conversation_history: List of previous messages [{'role': 'user'/'ai', 'text': '...'}]
            user_message: Latest user message
        
        Returns:
            str: AI response text
        """
        # Build conversation context
        context = f"Topic: {topic}\n\nConversation History:\n"
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            role = "User" if msg['role'] == 'user' else "AI"
            context += f"{role}: {msg['text']}\n"
        
        prompt = f"""
You are a friendly and helpful conversational AI assistant helping users improve their speech communication skills.

{context}

User just said: "{user_message}"

Respond naturally and engagingly:
1. Acknowledge what the user said
2. Ask follow-up questions to keep the conversation flowing
3. Provide relevant information or insights related to the topic
4. Encourage the user to speak more
5. Keep responses conversational and not too long (2-3 sentences)
6. Be supportive and encouraging

Your response:
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            raise Exception(f"Gemini conversation response failed: {str(e)}")
    
    def analyze_conversation(self, session, messages):
        """
        Analyze a completed conversation and provide feedback.
        
        Args:
            session: ConversationSession object
            messages: QuerySet of ConversationMessage objects
        
        Returns:
            dict: Feedback data with scores and analysis
        """
        # Build conversation transcript
        transcript = []
        user_messages = []
        
        for msg in messages:
            role = "User" if msg.role == 'user' else "AI"
            transcript.append(f"{role}: {msg.text}")
            if msg.role == 'user':
                user_messages.append(msg.text)
        
        conversation_text = "\n".join(transcript)
        
        prompt = f"""
You are an expert speech communication coach. Analyze this conversation and provide detailed feedback.

Topic: {session.topic.name if session.topic else 'General'}
Duration: {session.duration} seconds
Number of user messages: {session.user_message_count}

Conversation:
{conversation_text}

Provide a comprehensive analysis with scores (0-100) for:
1. Clarity - How clear and understandable was the speech
2. Fluency - How smooth and natural was the speaking
3. Vocabulary - Richness and appropriateness of word choice
4. Grammar - Grammatical accuracy
5. Confidence - Speaking confidence and assertiveness
6. Engagement - How engaged and interactive the user was

Also provide:
- Overall score (average of all scores)
- Detailed feedback (2-3 paragraphs)
- Strengths (bullet points)
- Areas for improvement (bullet points)
- Actionable tips (3-5 specific tips)

Return as JSON:
{{
    "overall_score": float,
    "clarity_score": float,
    "fluency_score": float,
    "vocabulary_score": float,
    "grammar_score": float,
    "confidence_score": float,
    "engagement_score": float,
    "feedback": "string",
    "strengths": "string (bullet points)",
    "improvements": "string (bullet points)",
    "tips": "string (bullet points)"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            feedback_data = json.loads(result_text.strip())
            return feedback_data
        
        except Exception as e:
            raise Exception(f"Gemini conversation analysis failed: {str(e)}")
    
    def generate_opening_message(self, topic):
        """
        Generate an opening message to start a conversation.
        
        Args:
            topic: Topic name
        
        Returns:
            str: Opening message
        """
        prompt = f"""
You are a friendly conversational AI assistant. Generate a warm, engaging opening message to start a conversation about: {topic}

The message should:
1. Greet the user warmly
2. Introduce the topic
3. Ask an open-ended question to get the conversation started
4. Be encouraging and friendly
5. Keep it brief (2-3 sentences)

Your opening message:
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            raise Exception(f"Gemini opening message generation failed: {str(e)}")
