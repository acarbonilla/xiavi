'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ConversationFeedback, ConversationMessage } from '@/types';
import { ArrowLeft, TrendingUp, Sparkles, Target, Lightbulb, MessageCircle } from 'lucide-react';
import Link from 'next/link';
import AudioPlayer from '@/components/AudioPlayer';

export default function FeedbackPage() {
    const params = useParams();
    const router = useRouter();
    const sessionId = parseInt(params.id as string);

    const [feedback, setFeedback] = useState<ConversationFeedback | null>(null);
    const [messages, setMessages] = useState<ConversationMessage[]>([]);
    const [vocabulary, setVocabulary] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<{ message: string; sessionStatus?: string } | null>(null);

    useEffect(() => {
        fetchData();
    }, [sessionId]);

    const fetchData = async () => {
        try {
            const [feedbackData, messagesData, vocabularyData] = await Promise.all([
                api.getConversationFeedback(sessionId),
                api.getConversationMessages(sessionId),
                api.getVocabulary({ source_session: sessionId })
            ]);
            setFeedback(feedbackData);
            setMessages(messagesData);
            setVocabulary(vocabularyData);
            setError(null);
        } catch (error: any) {
            console.error('Error fetching feedback:', error);

            // Extract error message from API response
            if (error.response?.data) {
                const errorData = error.response.data;
                setError({
                    message: errorData.error || 'Unable to load feedback',
                    sessionStatus: errorData.session_status
                });
            } else {
                setError({
                    message: 'Unable to load feedback. Please try again later.'
                });
            }
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-600';
        if (score >= 60) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getScoreBarColor = (score: number) => {
        if (score >= 80) return 'bg-green-500';
        if (score >= 60) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="max-w-md mx-auto text-center px-4">
                    <div className="card">
                        <div className="mb-6">
                            {error.sessionStatus === 'active' && (
                                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
                                    <span className="text-3xl">💬</span>
                                </div>
                            )}
                            {error.sessionStatus === 'incomplete' && (
                                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-100 mb-4">
                                    <span className="text-3xl">⏸️</span>
                                </div>
                            )}
                            {!error.sessionStatus || error.sessionStatus === 'completed' && (
                                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                                    <span className="text-3xl">📋</span>
                                </div>
                            )}

                            <h2 className="text-xl font-bold text-gray-900 mb-2">Feedback Not Available</h2>
                            <p className="text-gray-600 mb-6">{error.message}</p>
                        </div>

                        <div className="space-y-3">
                            {error.sessionStatus === 'active' && (
                                <Link href={`/conversation/${sessionId}`} className="btn-primary block">
                                    Continue Conversation
                                </Link>
                            )}
                            {error.sessionStatus === 'incomplete' && (
                                <Link href={`/conversation/${sessionId}`} className="btn-primary block">
                                    Resume Conversation
                                </Link>
                            )}
                            <Link href="/dashboard" className="btn-outline block">
                                Back to Dashboard
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!feedback) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <p className="text-gray-600 mb-4">Feedback not available</p>
                    <Link href="/dashboard" className="btn-primary">
                        Back to Dashboard
                    </Link>
                </div>
            </div>
        );
    }

    const skills = [
        { name: 'Clarity', score: feedback.clarity_score, icon: '🗣️' },
        { name: 'Fluency', score: feedback.fluency_score, icon: '⚡' },
        { name: 'Vocabulary', score: feedback.vocabulary_score, icon: '📚' },
        { name: 'Grammar', score: feedback.grammar_score, icon: '✍️' },
        { name: 'Confidence', score: feedback.confidence_score, icon: '💪' },
        { name: 'Engagement', score: feedback.engagement_score, icon: '🎯' },
    ];

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-4 py-4">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">Conversation Feedback</h1>
                            <p className="text-sm text-gray-600">{feedback.topic_name}</p>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
                {/* Overall Score */}
                <div className="card text-center">
                    <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br from-primary-500 to-purple-500 mb-4">
                        <div className="text-5xl font-bold text-white">
                            {Math.round(feedback.overall_score)}
                        </div>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Overall Score</h2>
                    <p className="text-gray-600">
                        {feedback.overall_score >= 80 ? 'Excellent!' :
                            feedback.overall_score >= 60 ? 'Good job!' :
                                'Keep practicing!'}
                    </p>
                </div>

                {/* Skill Scores */}
                <div className="card">
                    <div className="flex items-center space-x-2 mb-6">
                        <TrendingUp className="w-5 h-5 text-primary-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Skill Breakdown</h3>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {skills.map((skill) => (
                            <div key={skill.name}>
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-2xl">{skill.icon}</span>
                                        <span className="font-medium text-gray-900">{skill.name}</span>
                                    </div>
                                    <span className={`text-2xl font-bold ${getScoreColor(skill.score)}`}>
                                        {Math.round(skill.score)}
                                    </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                        className={`h-2 rounded-full ${getScoreBarColor(skill.score)} transition-all duration-500`}
                                        style={{ width: `${skill.score}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Detailed Feedback */}
                <div className="card">
                    <div className="flex items-center space-x-2 mb-4">
                        <Sparkles className="w-5 h-5 text-primary-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Detailed Feedback</h3>
                    </div>
                    <p className="text-gray-700 whitespace-pre-line">{feedback.feedback_text}</p>
                </div>

                {/* Strengths */}
                <div className="card bg-green-50 border-green-200">
                    <div className="flex items-center space-x-2 mb-4">
                        <Target className="w-5 h-5 text-green-600" />
                        <h3 className="text-lg font-semibold text-green-900">Strengths</h3>
                    </div>
                    <div className="text-green-800 whitespace-pre-line">{feedback.strengths}</div>
                </div>

                {/* Areas for Improvement */}
                <div className="card bg-yellow-50 border-yellow-200">
                    <div className="flex items-center space-x-2 mb-4">
                        <TrendingUp className="w-5 h-5 text-yellow-600" />
                        <h3 className="text-lg font-semibold text-yellow-900">Areas for Improvement</h3>
                    </div>
                    <div className="text-yellow-800 whitespace-pre-line">{feedback.improvements}</div>
                </div>

                {/* Tips */}
                <div className="card bg-primary-50 border-primary-200">
                    <div className="flex items-center space-x-2 mb-4">
                        <Lightbulb className="w-5 h-5 text-primary-600" />
                        <h3 className="text-lg font-semibold text-primary-900">Tips for Next Time</h3>
                    </div>
                    <div className="text-primary-800 whitespace-pre-line">{feedback.tips}</div>
                </div>

                {/* Suggested Vocabulary */}
                {vocabulary.length > 0 && (
                    <div className="card bg-indigo-50 border-indigo-200">
                        <div className="flex items-center space-x-2 mb-4">
                            <span className="text-2xl">📚</span>
                            <h3 className="text-lg font-semibold text-indigo-900">Suggested Vocabulary</h3>
                        </div>
                        <div className="space-y-4">
                            <p className="text-indigo-800 text-sm">
                                Based on your conversation, here are some words you might find useful:
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {vocabulary.map((item) => (
                                    <div key={item.id} className="bg-white p-4 rounded-lg shadow-sm border border-indigo-100">
                                        <div className="flex justify-between items-start mb-2">
                                            <h4 className="font-bold text-gray-900">{item.word}</h4>
                                            <span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
                                                New
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-600 mb-2">{item.definition}</p>
                                        {item.example_sentence && (
                                            <p className="text-xs text-gray-500 italic">"{item.example_sentence}"</p>
                                        )}
                                    </div>
                                ))}
                            </div>
                            <div className="text-center mt-4">
                                <Link href="/vocabulary" className="text-indigo-600 font-medium hover:text-indigo-800 text-sm">
                                    View all vocabulary →
                                </Link>
                            </div>
                        </div>
                    </div>
                )}

                {/* Filler Words */}
                {feedback.filler_word_count > 0 && (
                    <div className="card bg-blue-50 border-blue-200">
                        <div className="flex items-center space-x-2 mb-4">
                            <span className="text-2xl">💭</span>
                            <h3 className="text-lg font-semibold text-blue-900">Filler Word Analysis</h3>
                        </div>
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="text-center p-4 bg-white rounded-lg">
                                    <div className="text-3xl font-bold text-blue-900">{feedback.filler_word_count}</div>
                                    <div className="text-sm text-blue-700">Total Filler Words</div>
                                </div>
                                <div className="text-center p-4 bg-white rounded-lg">
                                    <div className="text-3xl font-bold text-blue-900">
                                        {feedback.filler_word_rate.toFixed(1)}
                                    </div>
                                    <div className="text-sm text-blue-700">Per Minute</div>
                                </div>
                            </div>

                            {Object.keys(feedback.filler_words_breakdown).length > 0 && (
                                <div className="bg-white rounded-lg p-4">
                                    <h4 className="font-semibold text-blue-900 mb-3">Breakdown:</h4>
                                    <div className="space-y-2">
                                        {Object.entries(feedback.filler_words_breakdown)
                                            .sort(([, a], [, b]) => (b as number) - (a as number))
                                            .map(([word, count]) => (
                                                <div key={word} className="flex items-center justify-between">
                                                    <span className="text-blue-800 font-medium capitalize">{word}</span>
                                                    <span className="px-3 py-1 bg-blue-100 text-blue-900 rounded-full text-sm font-semibold">
                                                        {count}
                                                    </span>
                                                </div>
                                            ))}
                                    </div>
                                </div>
                            )}

                            <p className="text-blue-800 text-sm">
                                💡 Try to reduce filler words by pausing and thinking before speaking. It's okay to have silence!
                            </p>
                        </div>
                    </div>
                )}

                {/* Transcript & Recordings */}
                <div className="card">
                    <div className="flex items-center space-x-2 mb-6">
                        <MessageCircle className="w-5 h-5 text-primary-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Conversation Transcript</h3>
                    </div>
                    <div className="space-y-6">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] ${msg.role === 'user' ? 'bg-primary-50' : 'bg-gray-50'} rounded-lg p-4`}>
                                    <div className="flex items-center space-x-2 mb-2">
                                        <span className={`text-xs font-bold uppercase ${msg.role === 'user' ? 'text-primary-700' : 'text-gray-700'}`}>
                                            {msg.role === 'user' ? 'You' : 'AI Coach'}
                                        </span>
                                        <span className="text-xs text-gray-500">
                                            {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                    </div>
                                    <p className="text-gray-800 whitespace-pre-wrap mb-3">{msg.text}</p>

                                    {msg.role === 'user' && msg.audio_file && (
                                        <div className="mt-2">
                                            <AudioPlayer audioUrl={msg.audio_file} />
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Actions */}
                <div className="flex justify-center space-x-4">
                    <Link href="/dashboard" className="btn-primary">
                        Start New Conversation
                    </Link>
                    <Link href="/history" className="btn-outline">
                        View History
                    </Link>
                </div>
            </div>
        </div>
    );
}
