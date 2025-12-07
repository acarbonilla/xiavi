"""
Gemini Conversational AI Service
Features:
- Ultra-Natural RAG Blending
- Short- & Long-Term Memory
- Emotional Tone Tracking
- Conversation Depth Modeling
- Adaptive English Difficulty
- Topic Personality Presets
- Human-Like Follow-Up Questions
- Smart Correction Behavior (“Is that correct?” / “Okay na ba?” logic)
"""

import json
from typing import List, Dict
import numpy as np
import google.generativeai as genai
from django.conf import settings


class GeminiService:
    PERSONALITY_PRESETS = {
        "travel": "You sound curious, open-minded, fun, and a bit adventurous.",
        "workplace": "You sound polite, steady, supportive, and professional but still friendly.",
        "casual": "You sound relaxed, simple, and natural like everyday conversation.",
        "motivation": "You sound warm, encouraging, and supportive — not overly dramatic.",
        "study": "You sound patient, clear, and student-friendly.",
    }

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("models/gemini-2.0-flash")
        self.embedding_model = "models/text-embedding-004"

    # ============================================================
    # Embeddings + Similarity
    # ============================================================
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0

        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def generate_query_embedding(self, query: str):
        result = genai.embed_content(
            model=self.embedding_model,
            content=query,
            task_type="retrieval_query",
        )
        return result["embedding"]

    # ============================================================
    # RAG Chunk Retrieval
    # ============================================================
    def retrieve_relevant_chunks(self, session, user_message: str, top_k=3):
        from apps.conversations.models import DocumentChunk

        chunks = (
            DocumentChunk.objects.filter(
                document__session=session, document__processed=True
            )
            .select_related("document")
        )

        if not chunks.exists():
            return []

        query_emb = self.generate_query_embedding(user_message)

        scored = []
        for chunk in chunks:
            try:
                sim = self.cosine_similarity(query_emb, chunk.embedding)
                scored.append(
                    {
                        "text": chunk.text,
                        "filename": chunk.document.filename,
                        "similarity": sim,
                    }
                )
            except:
                continue

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    # ============================================================
    # Filler Word Detector
    # ============================================================
    def _detect_filler_words(self, text, duration_seconds):
        import re

        fillers = {
            "um": r"\bum+\b",
            "uh": r"\buh+\b",
            "like": r"\blike\b",
            "you know": r"\byou know\b",
            "so": r"\bso\b",
        }

        breakdown = {}
        total = 0
        lowered = text.lower()

        for word, pattern in fillers.items():
            count = len(re.findall(pattern, lowered))
            if count > 0:
                breakdown[word] = count
                total += count

        minutes = max((duration_seconds or 60) / 60, 1)
        return {
            "total_count": total,
            "rate_per_minute": total / minutes,
            "breakdown": breakdown,
        }

    # ============================================================
    # MAIN CONVERSATION METHOD
    # ============================================================
    def generate_conversation_response(
        self, topic, conversation_history, user_message, session=None
    ):

        # ----------------------------
        # Context Window
        # ----------------------------
        context = "Topic: {}\n\nConversation History:\n".format(topic)
        for msg in conversation_history[-5:]:
            role = "User" if msg["role"] == "user" else "AI"
            context += f"{role}: {msg['text']}\n"

        # ----------------------------
        # Personality Preset
        # ----------------------------
        personality = self.PERSONALITY_PRESETS.get(
            (topic or "").lower(), "You sound friendly, relaxed, and easy to talk to."
        )

        # ----------------------------
        # Short-Term Memory
        # ----------------------------
        memory = []
        if session:
            memory = session.conversation_memory or []
            if len(memory) > 8:
                memory.pop(0)
            memory.append(user_message)
            session.conversation_memory = memory
            session.save()
        memory_block = memory

        # ----------------------------
        # Long-Term User Memory
        # ----------------------------
        user = getattr(session, "user", None) if session else None
        long_term_memory = {}
        if user and hasattr(user, "long_term_memory"):
            long_term_memory = user.long_term_memory or {}

        # ----------------------------
        # Emotional Tone Tracking
        # ----------------------------
        emotion = "neutral"
        if session:
            try:
                emotion_prompt = f"""
Classify the emotion of this message:
Options: happy, neutral, confused, frustrated, tired, excited, worried.
Message: "{user_message}"
Return one word only.
"""
                emotion = (
                    self.model.generate_content(emotion_prompt).text.strip().lower()
                )
            except:
                emotion = "neutral"

            if emotion not in [
                "happy",
                "neutral",
                "confused",
                "frustrated",
                "tired",
                "excited",
                "worried",
            ]:
                emotion = "neutral"

            trend = session.emotion_trend or []
            trend.append(emotion)
            if len(trend) > 20:
                trend.pop(0)
            session.emotion_trend = trend
            session.save()
        else:
            trend = []

        # ----------------------------
        # Conversation Depth
        # ----------------------------
        depth = session.conversation_depth if session else 0
        if any(
            key in user_message.lower()
            for key in ["why", "because", "i feel", "i think", "my experience"]
        ):
            depth += 1
        else:
            depth = max(depth - 1, 0)

        if session:
            session.conversation_depth = depth
            session.save()

        # ----------------------------
        # Adaptive Difficulty
        # ----------------------------
        difficulty = "beginner"
        if user and hasattr(user, "difficulty_level"):
            difficulty = user.difficulty_level or "beginner"

        if len(user_message.split()) > 12:
            difficulty = "intermediate"

        if any(
            w in user_message.lower()
            for w in ["analyze", "situation", "process", "experience"]
        ):
            difficulty = "advanced"

        if user and hasattr(user, "difficulty_level"):
            if user.difficulty_level != difficulty:
                user.difficulty_level = difficulty
                user.save()

        # ----------------------------
        # RAG
        # ----------------------------
        document_context = ""
        referenced_docs = []

        if session:
            chunks = self.retrieve_relevant_chunks(session, user_message)
            good_chunks = [c for c in chunks if c["similarity"] > 0.30]

            if good_chunks:
                document_context = "\nDocument Excerpts (summarized):\n"
                seen = set()
                for c in good_chunks:
                    summary = c["text"][:350]
                    document_context += f"- {summary}\n"
                    if c["filename"] not in seen:
                        referenced_docs.append(c["filename"])
                        seen.add(c["filename"])

        # ----------------------------
        # MAIN PROMPT
        # ----------------------------
        prompt = f"""
You are a friendly, relaxed conversational partner.

Tone Personality:
{personality}

Short-Term Memory:
{memory_block}

Long-Term Memory:
{long_term_memory}

Emotional Trend:
{trend}

Conversation Depth: {depth}
- 0–1 → light conversation
- 2–3 → reflective
- 4+ → deeper emotional style

User English Level: {difficulty}

Adaptive English Rules:
- beginner → use simpler vocabulary and short sentences
- intermediate → normal everyday English
- advanced → richer and more nuanced wording

Ultra-Natural RAG Behavior:
- Use excerpts only when clearly relevant.
- Integrate knowledge naturally.
- Do NOT mention “documents” or “sources.”

Follow-Up Behavior:
- Ask ONE natural follow-up IF it flows.
- Never force drills.
- Never shift topic unless the user does.

Correction Behavior:
- If the user says: “Is that correct?”, “Okay na ba?”, “Tama na ba ito?”, or similar:
    • Confirm correctness warmly.
    • Do NOT ask them to repeat again.
    • Do NOT start new drills unless they ask.
    • Shift to supportive tone.

{document_context}

{context}

User said: "{user_message}"

Your response (2–4 sentences, natural, supportive, human-like):
"""

        # ----------------------------
        # Generate Response
        # ----------------------------
        reply = self.model.generate_content(prompt).text.strip()

        # ----------------------------
        # Update Long-Term Memory Simple Markers
        # ----------------------------
        if user and hasattr(user, "long_term_memory"):
            updated = dict(long_term_memory)
            low = user_message.lower()

            if "travel" in low:
                updated["likes_travel"] = True
            if "practice" in low:
                updated["active_learner"] = True
            if any(w in low for w in ["hard", "hirap", "difficult"]):
                updated["struggle_flag"] = True

            if updated != long_term_memory:
                user.long_term_memory = updated
                user.save()

        return {"response": reply, "referenced_documents": referenced_docs}

    # ============================================================
    # Conversation Analysis
    # ============================================================
    def analyze_conversation(self, session, messages):
        transcript = []
        user_text = ""

        for m in messages:
            role = "User" if m.role == "user" else "AI"
            transcript.append(f"{role}: {m.text}")
            if m.role == "user":
                user_text += " " + m.text

        transcript_text = "\n".join(transcript)[-8000:]
        filler_stats = self._detect_filler_words(user_text, session.duration or 60)

        prompt = f"""
You are an English communication evaluator.

Conversation:
{transcript_text}

Filler Words:
{filler_stats}

Return JSON ONLY with:
overall_score,
clarity_score,
fluency_score,
vocabulary_score,
grammar_score,
confidence_score,
engagement_score,
feedback,
strengths,
improvements,
tips,
suggested_vocabulary.
"""

        response = self.model.generate-content(prompt)
        text = response.text.strip()

        # cleanup
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        try:
            data = json.loads(text)
        except:
            # Safe fallback
            data = {
                "overall_score": 50,
                "clarity_score": 50,
                "fluency_score": 50,
                "vocabulary_score": 50,
                "grammar_score": 50,
                "confidence_score": 50,
                "engagement_score": 50,
                "feedback": "Automatic fallback. Analysis failed.",
                "strengths": "",
                "improvements": "",
                "tips": "",
                "suggested_vocabulary": [],
            }

        return data

    # ============================================================
    # Opening Message Generator
    # ============================================================
    def generate_opening_message(self, topic):
        personality = self.PERSONALITY_PRESETS.get(
            (topic or "").lower(), "You sound relaxed, friendly, and welcoming."
        )

        prompt = f"""
Create a short (1–2 sentence) warm, natural opening message.
Tone: {personality}
Topic: {topic}
Avoid sounding formal or like an exam.
"""

        return self.model.generate_content(prompt).text.strip()

    # ============================================================
    # Teacher Mode
    # ============================================================
    def generate_classroom_response(self, topic, conversation_history, user_message):
        context = ""
        for msg in conversation_history[-5:]:
            r = "User" if msg["role"] == "user" else "Teacher"
            context += f"{r}: {msg['text']}\n"

        prompt = f"""
You are a kind English teacher.

Student said: "{user_message}"

Perform:
1. A corrected sentence if needed.
2. A short explanation (1–2 sentences).
3. A natural reply + one practice question.

Return ONLY JSON:
{{
  "response": "...",
  "correction": "... or null",
  "explanation": "... or null"
}}
"""

        raw = self.model.generate_content(prompt).text.strip()

        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]

        try:
            return json.loads(raw)
        except:
            return {
                "response": "I understood your message but couldn't analyze it. Try rephrasing?",
                "correction": None,
                "explanation": None,
            }
