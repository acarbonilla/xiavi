'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ConversationFeedback } from '@/types';
import { ArrowLeft, TrendingUp, Sparkles, Target, Lightbulb } from 'lucide-react';
import Link from 'next/link';

export default function FeedbackPage() {
    const params = useParams();
    const router = useRouter();
    const sessionId = parseInt(params.id as string);

    const [feedback, setFeedback] = useState<ConversationFeedback | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchFeedback();
    }, [sessionId]);

    const fetchFeedback = async () => {
        try {
            const data = await api.getConversationFeedback(sessionId);
            setFeedback(data);
        } catch (error) {
            console.error('Error fetching feedback:', error);
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
