'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ConversationSession } from '@/types';
import { ArrowLeft, Clock, MessageCircle, Play, Trash2 } from 'lucide-react';
import Link from 'next/link';

export default function ResumePage() {
    const router = useRouter();
    const [sessions, setSessions] = useState<ConversationSession[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchSessions();
    }, []);

    const fetchSessions = async () => {
        try {
            const data = await api.getConversations({ status: 'incomplete' });
            setSessions(data);
        } catch (error) {
            console.error('Error fetching incomplete sessions:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleResume = (sessionId: number) => {
        router.push(`/conversation/${sessionId}`);
    };

    const handleDelete = async (sessionId: number) => {
        if (!confirm('Are you sure you want to delete this conversation? This cannot be undone.')) {
            return;
        }

        try {
            await api.deleteConversation(sessionId);
            setSessions(prev => prev.filter(s => s.id !== sessionId));
        } catch (error) {
            console.error('Error deleting session:', error);
            alert('Failed to delete conversation');
        }
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
            <header className="bg-white border-b border-gray-200 px-4 py-4">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">Resume Conversations</h1>
                            <p className="text-sm text-gray-600">
                                Continue where you left off
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-4xl mx-auto px-4 py-8">
                {sessions.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
                        <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No incomplete conversations</h3>
                        <p className="text-gray-500 mb-6">You don't have any conversations to resume.</p>
                        <Link href="/dashboard" className="btn-primary">
                            Start New Conversation
                        </Link>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {sessions.map((session) => (
                            <div
                                key={session.id}
                                className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                                                Incomplete
                                            </span>
                                            <span className="text-sm text-gray-500 flex items-center">
                                                <Clock className="w-3 h-3 mr-1" />
                                                {new Date(session.started_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                                            {session.topic_name || 'Untitled Conversation'}
                                        </h3>
                                        <p className="text-sm text-gray-600">
                                            {session.message_count} messages exchanged
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => handleDelete(session.id)}
                                        className="btn-outline flex items-center space-x-2 px-4 py-2 ml-2"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                        <span>Delete</span>
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
