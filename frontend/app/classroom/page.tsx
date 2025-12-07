'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { BookOpen, MessageCircle, ArrowRight } from 'lucide-react';
import Navbar from '@/components/Navbar';

export default function ClassroomPage() {
    const { isAuthenticated, loading: authLoading } = useAuth();
    const router = useRouter();
    const [topics, setTopics] = useState<any[]>([]);
    const [sessions, setSessions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [startingSession, setStartingSession] = useState(false);

    useEffect(() => {
        if (authLoading) return;

        if (!isAuthenticated) {
            router.push('/login');
            return;
        }

        const fetchData = async () => {
            try {
                const [topicsData, sessionsData] = await Promise.all([
                    api.getTopics(),
                    api.getClassroomSessions()
                ]);
                setTopics(topicsData);
                setSessions(sessionsData);
            } catch (error) {
                console.error('Error fetching classroom data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [isAuthenticated, authLoading, router]);

    const handleStartSession = async (topicId: number) => {
        setStartingSession(true);
        try {
            const session = await api.startClassroomSession(topicId);
            router.push(`/classroom/${session.id}`);
        } catch (error) {
            console.error('Error starting session:', error);
            setStartingSession(false);
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
            <Navbar />
            <div className="py-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-12">
                        <h1 className="text-4xl font-bold text-gray-900 mb-4">AI Classroom</h1>
                        <p className="text-xl text-gray-600">Learn communication skills with your personal AI teacher.</p>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Lessons / Topics */}
                        <div className="lg:col-span-2">
                            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                                <BookOpen className="w-6 h-6 mr-2 text-primary-600" />
                                Available Lessons
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {topics.map((topic) => (
                                    <div key={topic.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className={`p-3 rounded-lg bg-${topic.color || 'blue'}-100 text-${topic.color || 'blue'}-600`}>
                                                <MessageCircle className="w-6 h-6" />
                                            </div>
                                            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium capitalize
                                            ${topic.difficulty === 'advanced' ? 'bg-red-100 text-red-800' :
                                                    topic.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                                                        'bg-green-100 text-green-800'}`}>
                                                {topic.difficulty}
                                            </span>
                                        </div>
                                        <h3 className="text-lg font-bold text-gray-900 mb-2">{topic.name}</h3>
                                        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{topic.description}</p>
                                        <button
                                            onClick={() => handleStartSession(topic.id)}
                                            disabled={startingSession}
                                            className="w-full flex items-center justify-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors font-medium"
                                        >
                                            <span>Start Class</span>
                                            <ArrowRight className="w-4 h-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Recent Sessions */}
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                                <MessageCircle className="w-6 h-6 mr-2 text-primary-600" />
                                Recent Classes
                            </h2>
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                {sessions.length > 0 ? (
                                    <ul className="divide-y divide-gray-200">
                                        {sessions.map((session) => (
                                            <li key={session.id}>
                                                <a href={`/classroom/${session.id}`} className="block hover:bg-gray-50 p-4">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className={`px-2 py-0.5 rounded text-xs font-bold capitalize
                                                        ${session.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
                                                            {session.status}
                                                        </span>
                                                        <span className="text-xs text-gray-500">
                                                            {new Date(session.created_at).toLocaleDateString()}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm font-medium text-gray-900">
                                                        {session.topic?.name || 'General Class'}
                                                    </p>
                                                </a>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <div className="p-8 text-center text-gray-500">
                                        No classes taken yet.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
