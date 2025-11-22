'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { Topic, ConversationSession, LearnerProfile } from '@/types';
import { useRouter } from 'next/navigation';
import {
    MessageCircle,
    TrendingUp,
    Clock,
    Flame,
    LogOut,
    Sparkles,
    Play,
    History,
    BarChart3
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
    const { user, logout, isAuthenticated } = useAuth();
    const router = useRouter();
    const [topics, setTopics] = useState<Topic[]>([]);
    const [recentConversations, setRecentConversations] = useState<ConversationSession[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }

        const fetchData = async () => {
            try {
                const [topicsData, conversationsData] = await Promise.all([
                    api.getTopics(),
                    api.getConversations({ status: 'completed' })
                ]);
                setTopics(topicsData);
                setRecentConversations(conversationsData.slice(0, 5));
            } catch (error) {
                console.error('Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [isAuthenticated, router]);

    const handleStartConversation = async (topicId: number) => {
        try {
            const session = await api.startConversation(topicId);
            router.push(`/conversation/${session.id}`);
        } catch (error) {
            console.error('Error starting conversation:', error);
        }
    };

    const profile = user?.learner_profile;

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'beginner': return 'bg-green-100 text-green-700';
            case 'intermediate': return 'bg-yellow-100 text-yellow-700';
            case 'advanced': return 'bg-red-100 text-red-700';
            default: return 'bg-gray-100 text-gray-700';
        }
    };

    const getTopicColor = (color: string) => {
        const colors: Record<string, string> = {
            blue: 'from-blue-500 to-blue-600',
            purple: 'from-purple-500 to-purple-600',
            green: 'from-green-500 to-green-600',
            orange: 'from-orange-500 to-orange-600',
            red: 'from-red-500 to-red-600',
        };
        return colors[color] || 'from-primary-500 to-primary-600';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-3">
                            <MessageCircle className="w-8 h-8 text-primary-600" />
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">
                                    Welcome back, {user?.first_name}!
                                </h1>
                                <p className="text-sm text-gray-600 capitalize">
                                    {user?.language_level} Level
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={logout}
                            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                        >
                            <LogOut className="w-5 h-5" />
                            <span>Logout</span>
                        </button>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="card">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Total Conversations</p>
                                <p className="text-3xl font-bold text-gray-900">
                                    {profile?.total_conversations || 0}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                                <MessageCircle className="w-6 h-6 text-primary-600" />
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Speaking Time</p>
                                <p className="text-3xl font-bold text-gray-900">
                                    {Math.floor((profile?.total_speaking_time || 0) / 60)}m
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                                <Clock className="w-6 h-6 text-purple-600" />
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Current Streak</p>
                                <p className="text-3xl font-bold text-gray-900">
                                    {profile?.current_streak || 0}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                                <Flame className="w-6 h-6 text-orange-600" />
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Overall Score</p>
                                <p className="text-3xl font-bold text-gray-900">
                                    {profile?.skill_scores ?
                                        Math.round(Object.values(profile.skill_scores).reduce((a, b) => a + b, 0) / 6) :
                                        0}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                                <TrendingUp className="w-6 h-6 text-green-600" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Topics Section */}
                    <div className="lg:col-span-2">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold text-gray-900">Choose a Topic</h2>
                            <Sparkles className="w-6 h-6 text-primary-600" />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {topics.map((topic) => (
                                <div
                                    key={topic.id}
                                    className="card group hover:scale-105 transition-all duration-200 cursor-pointer"
                                    onClick={() => handleStartConversation(topic.id)}
                                >
                                    <div className={`w-full h-2 rounded-t-lg bg-gradient-to-r ${getTopicColor(topic.color)} -mt-6 -mx-6 mb-4`}></div>
                                    <div className="flex items-start justify-between mb-3">
                                        <h3 className="text-xl font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                                            {topic.name}
                                        </h3>
                                        <span className={`badge ${getDifficultyColor(topic.difficulty)} capitalize text-xs`}>
                                            {topic.difficulty}
                                        </span>
                                    </div>
                                    <p className="text-gray-600 text-sm mb-4">
                                        {topic.description}
                                    </p>
                                    <div className="flex items-center justify-between">
                                        <span className="text-xs text-gray-500">
                                            {topic.conversation_count} conversations
                                        </span>
                                        <button className="btn-primary py-2 px-4 text-sm flex items-center space-x-2">
                                            <Play className="w-4 h-4" />
                                            <span>Start</span>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Recent Conversations */}
                        <div className="card">
                            <div className="flex items-center space-x-2 mb-4">
                                <History className="w-5 h-5 text-gray-600" />
                                <h3 className="text-lg font-semibold text-gray-900">Recent</h3>
                            </div>
                            {recentConversations.length > 0 ? (
                                <div className="space-y-3">
                                    {recentConversations.map((conv) => (
                                        <Link
                                            key={conv.id}
                                            href={`/conversation/${conv.id}/feedback`}
                                            className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                                        >
                                            <p className="font-medium text-gray-900 text-sm">{conv.topic_name}</p>
                                            <p className="text-xs text-gray-500">
                                                {conv.message_count} messages · {Math.floor(conv.duration / 60)}m
                                            </p>
                                        </Link>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-500 text-sm">No conversations yet</p>
                            )}
                            <Link href="/history" className="block mt-4 text-primary-600 hover:text-primary-700 text-sm font-semibold">
                                View All →
                            </Link>
                        </div>

                        {/* Quick Actions */}
                        <div className="card">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                            <div className="space-y-2">
                                <Link href="/history" className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                    <History className="w-5 h-5 text-gray-600" />
                                    <span className="text-sm font-medium text-gray-900">Conversation History</span>
                                </Link>
                                <Link href="/progress" className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                    <BarChart3 className="w-5 h-5 text-gray-600" />
                                    <span className="text-sm font-medium text-gray-900">View Progress</span>
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
