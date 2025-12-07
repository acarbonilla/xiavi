import axios, { AxiosInstance, AxiosError } from 'axios';
import {
    User,
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    Topic,
    ConversationSession,
    ConversationMessage,
    ConversationFeedback,
    Voice,
    Scenario,
    VocabularyItem
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export class APIClient {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Request interceptor to add auth token
        this.client.interceptors.request.use(
            (config) => {
                const token = this.getAccessToken();
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // Response interceptor to handle token refresh
        this.client.interceptors.response.use(
            (response) => response,
            async (error: AxiosError) => {
                const originalRequest = error.config as any;

                if (error.response?.status === 401 && !originalRequest._retry) {
                    originalRequest._retry = true;

                    try {
                        const refreshToken = this.getRefreshToken();
                        if (refreshToken) {
                            const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
                                refresh: refreshToken,
                            });

                            const { access } = response.data;
                            this.setAccessToken(access);

                            originalRequest.headers.Authorization = `Bearer ${access}`;
                            return this.client(originalRequest);
                        }
                    } catch (refreshError) {
                        this.clearTokens();
                        window.location.href = '/login';
                        return Promise.reject(refreshError);
                    }
                }

                return Promise.reject(error);
            }
        );
    }

    // Token management
    private getAccessToken(): string | null {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('access_token');
        }
        return null;
    }

    private getRefreshToken(): string | null {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('refresh_token');
        }
        return null;
    }

    private setAccessToken(token: string): void {
        if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', token);
        }
    }

    private setRefreshToken(token: string): void {
        if (typeof window !== 'undefined') {
            localStorage.setItem('refresh_token', token);
        }
    }

    private clearTokens(): void {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
        }
    }

    // Authentication
    async login(data: LoginRequest): Promise<AuthResponse> {
        const response = await this.client.post<AuthResponse>('/auth/login/', data);
        this.setAccessToken(response.data.access);
        this.setRefreshToken(response.data.refresh);
        if (typeof window !== 'undefined') {
            localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        return response.data;
    }

    async register(data: RegisterRequest): Promise<User> {
        const response = await this.client.post<User>('/auth/register/', data);
        return response.data;
    }

    async logout(): Promise<void> {
        const refreshToken = this.getRefreshToken();
        if (refreshToken) {
            try {
                await this.client.post('/auth/logout/', { refresh: refreshToken });
            } catch (error) {
                console.error('Logout error:', error);
            }
        }
        this.clearTokens();
    }

    async getProfile(): Promise<User> {
        const response = await this.client.get<User>('/auth/profile/');
        return response.data;
    }

    async changePassword(oldPassword: string, newPassword: string): Promise<void> {
        await this.client.post('/auth/change-password/', {
            old_password: oldPassword,
            new_password: newPassword,
        });
    }

    // Topics
    async getTopics(): Promise<Topic[]> {
        const response = await this.client.get<any>('/conversations/topics/');
        return response.data.results || response.data;
    }

    async getTopic(id: number): Promise<Topic> {
        const response = await this.client.get<Topic>(`/conversations/topics/${id}/`);
        return response.data;
    }

    // Scenarios
    async getScenarios(): Promise<Scenario[]> {
        const response = await this.client.get<any>('/training/scenarios/');
        return response.data.results || response.data;
    }

    // Conversation Sessions
    async getConversations(params?: { status?: string }): Promise<ConversationSession[]> {
        const response = await this.client.get<any>('/conversations/sessions/', { params });
        return response.data.results || response.data;
    }

    async getConversation(id: number): Promise<ConversationSession> {
        const response = await this.client.get<ConversationSession>(`/conversations/sessions/${id}/`);
        return response.data;
    }

    async startConversation(topicId?: number, scenarioId?: number, voiceId?: string): Promise<ConversationSession> {
        const response = await this.client.post<ConversationSession>('/conversations/sessions/start_conversation/', {
            topic_id: topicId,
            scenario_id: scenarioId,
            voice_id: voiceId
        });
        return response.data;
    }

    async getConversationMessages(sessionId: number): Promise<ConversationMessage[]> {
        const response = await this.client.get<ConversationMessage[]>(`/conversations/sessions/${sessionId}/messages/`);
        return response.data;
    }

    async sendAudioMessage(sessionId: number, audioBlob: Blob, duration: number): Promise<any> {
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.webm');
        formData.append('duration', duration.toString());

        const response = await this.client.post(`/conversations/sessions/${sessionId}/speak/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }

    async endConversation(sessionId: number): Promise<void> {
        await this.client.post(`/conversations/sessions/${sessionId}/end/`);
    }

    async getConversationFeedback(sessionId: number): Promise<ConversationFeedback> {
        const response = await this.client.get<ConversationFeedback>(`/conversations/sessions/${sessionId}/feedback/`);
        return response.data;
    }

    async markSessionIncomplete(sessionId: number): Promise<void> {
        await this.client.post(`/conversations/sessions/${sessionId}/mark_incomplete/`);
    }

    async deleteConversation(sessionId: number): Promise<void> {
        await this.client.delete(`/conversations/sessions/${sessionId}/`);
    }

    // Document Management
    async uploadDocument(sessionId: number, file: File): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await this.client.post(
            `/conversations/sessions/${sessionId}/upload_document/`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );
        return response.data;
    }

    async getDocuments(sessionId: number): Promise<any[]> {
        const response = await this.client.get(
            `/conversations/sessions/${sessionId}/documents/`
        );
        return response.data;
    }

    async deleteDocument(documentId: number): Promise<void> {
        await this.client.delete(`/conversations/sessions/documents/${documentId}/`);
    }

    // Voice Management
    async getVoices(): Promise<Voice[]> {
        const response = await this.client.get<{ voices: Voice[] }>('/conversations/voices/');
        return response.data.voices;
    }

    async updateProfile(data: Partial<User>): Promise<User> {
        const response = await this.client.patch<User>('/auth/profile/', data);
        return response.data;
    }

    async previewVoice(voiceId: string, sampleText: string = "Hello! This is a preview of my voice. I'm excited to help you practice your English communication skills."): Promise<ArrayBuffer> {
        // This would require a backend endpoint to generate preview audio
        // For now, we'll use the existing TTS by creating a temporary session
        // In production, you might want a dedicated preview endpoint
        const response = await this.client.post(
            '/conversations/preview-voice/',
            { voice_id: voiceId, text: sampleText },
            { responseType: 'arraybuffer' }
        );
        return response.data;
    }

    // Training
    async getTrainingSessions(): Promise<any[]> {
        const response = await this.client.get('/training/sessions/');
        return response.data.results || response.data;
    }

    async getTrainingSession(id: number): Promise<any> {
        const response = await this.client.get(`/training/sessions/${id}/`);
        return response.data;
    }

    async startTrainingSession(questionId: number): Promise<any> {
        const response = await this.client.post('/training/sessions/', {
            question: questionId
        });
        return response.data;
    }

    async completeTrainingSession(sessionId: number): Promise<any> {
        const response = await this.client.post(`/training/sessions/${sessionId}/complete/`);
        return response.data;
    }

    async generateTrainingFeedback(sessionId: number, videoBlob: Blob): Promise<any> {
        const formData = new FormData();
        formData.append('video_file', videoBlob, 'training.webm');
        formData.append('session_id', sessionId.toString());

        const response = await this.client.post(
            '/training/feedback/generate/',
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );
        return response.data;
    }

    // Questions
    async getQuestions(type?: string): Promise<any[]> {
        const params = type ? { type } : {};
        const response = await this.client.get('/questions/questions/', { params });
        return response.data.results || response.data;
    }

    // Goal Tracking
    async getGoalStatus(): Promise<any> {
        const response = await this.client.get('/auth/profile/goal-status/');
        return response.data;
    }

    async setDailyGoals(minutes: number, conversations: number): Promise<any> {
        const response = await this.client.patch('/auth/profile/set-goals/', {
            daily_goal_minutes: minutes,
            daily_goal_conversations: conversations
        });
        return response.data;
    }

    async getStreakHistory(days: number = 30): Promise<any[]> {
        const response = await this.client.get('/auth/profile/streak-history/', {
            params: { days }
        });
        return response.data;
    }

    // Analytics
    async getAnalytics(days: number = 30): Promise<any> {
        const response = await this.client.get('/conversations/sessions/analytics/', {
            params: { days }
        });
        return response.data;
    }

    // Vocabulary
    async getVocabulary(params?: { mastery_level?: number, search?: string, source_session?: number }): Promise<VocabularyItem[]> {
        const response = await this.client.get<any>('/learning/vocabulary/', { params });
        return response.data.results || response.data;
    }

    async addVocabularyItem(data: Partial<VocabularyItem>): Promise<VocabularyItem> {
        const response = await this.client.post<VocabularyItem>('/learning/vocabulary/', data);
        return response.data;
    }

    async updateVocabularyItem(id: number, data: Partial<VocabularyItem>): Promise<VocabularyItem> {
        const response = await this.client.patch<VocabularyItem>(`/learning/vocabulary/${id}/`, data);
        return response.data;
    }

    async deleteVocabularyItem(id: number): Promise<void> {
        await this.client.delete(`/learning/vocabulary/${id}/`);
    }

    async markVocabularyReviewed(id: number): Promise<void> {
        await this.client.post(`/learning/vocabulary/${id}/mark_reviewed/`);
    }

    async updateVocabularyMastery(id: number, correct: boolean): Promise<VocabularyItem> {
        const response = await this.client.post<VocabularyItem>(`/learning/vocabulary/${id}/update_mastery/`, { correct });
        return response.data;
    }

    // Classroom
    async getClassroomSessions(): Promise<any[]> {
        const response = await this.client.get('/classroom/sessions/');
        return response.data.results || response.data;
    }

    async getClassroomSession(id: number): Promise<any> {
        const response = await this.client.get(`/classroom/sessions/${id}/`);
        return response.data;
    }

    async startClassroomSession(topicId: number): Promise<any> {
        const response = await this.client.post('/classroom/sessions/', {
            topic_id: topicId
        });
        return response.data;
    }

    async sendClassroomMessage(sessionId: number, message: string): Promise<any> {
        const response = await this.client.post(`/classroom/sessions/${sessionId}/send_message/`, {
            message
        });
        return response.data;
    }
}

export const api = new APIClient();
