export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  language_level: 'beginner' | 'intermediate' | 'advanced';
  native_language: string;
  target_language: string;
  phone?: string;
  learner_profile?: LearnerProfile;
  created_at: string;
}

export interface LearnerProfile {
  bio?: string;
  total_conversations: number;
  total_speaking_time: number;
  current_streak: number;
  longest_streak: number;
  topics_covered: Record<string, number>;
  skill_scores: SkillScores;
  last_conversation_date?: string;
  preferred_voice: string;
}

export interface SkillScores {
  clarity: number;
  fluency: number;
  vocabulary: number;
  grammar: number;
  confidence: number;
  engagement: number;
}

export interface Topic {
  id: number;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  icon: string;
  color: string;
  is_active: boolean;
  conversation_count: number;
  created_at: string;
}

export interface Scenario {
  id: number;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  system_prompt: string;
  initial_message: string;
  objectives: string[];
  icon: string;
  is_active: boolean;
  created_at: string;
}

export interface ConversationSession {
  id: number;
  user: number;
  topic: number;
  topic_name?: string;
  status: 'active' | 'completed';
  started_at: string;
  ended_at?: string;
  duration: number;
  message_count: number;
  user_message_count: number;
  total_speaking_time: number;
  voice_preference?: string;
  messages?: ConversationMessage[];
}

export interface ConversationMessage {
  id: number;
  session: number;
  role: 'user' | 'ai';
  text: string;
  audio_file?: string;
  duration: number;
  timestamp: string;
  referenced_documents?: string[];
}

export interface ConversationFeedback {
  id: number;
  session: number;
  session_id?: number;
  topic_name?: string;
  overall_score: number;
  clarity_score: number;
  fluency_score: number;
  vocabulary_score: number;
  grammar_score: number;
  confidence_score: number;
  engagement_score: number;
  feedback_text: string;
  strengths: string;
  improvements: string;
  tips: string;
  filler_word_count: number;
  filler_word_rate: number;
  filler_words_breakdown: Record<string, number>;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
  language_level: 'beginner' | 'intermediate' | 'advanced';
  native_language?: string;
  target_language?: string;
  phone?: string;
}

export interface AuthResponse {
  refresh: string;
  access: string;
  user: User;
}

export interface Voice {
  id: string;
  name: string;
  description: string;
  google_voice: string;
  gender: 'male' | 'female';
  tone: string;
  pitch_range: string;
}

export interface VocabularyItem {
  id: number;
  word: string;
  definition: string;
  example_sentence: string;
  translation?: string;
  mastery_level: number;
  review_count: number;
  times_correct: number;
  created_at: string;
  last_reviewed_at?: string;
}
