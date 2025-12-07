'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { BookOpen, Play, Clock, CheckCircle, Video, Mic } from 'lucide-react';
import Link from 'next/link';

export default function TrainingPage() {
    const { user, isAuthenticated } = useAuth();
    const router = useRouter();
    const [sessions, setSessions] = useState<any[]>([]);
    const [questions, setQuestions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [startingSession, setStartingSession] = useState(false);

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }

        const fetchData = async () => {
            try {
                const [sessionsData, questionsData] = await Promise.all([
                    api.getTrainingSessions(),
                    api.getQuestions()
                ]);
                setSessions(sessionsData);
                setQuestions(questionsData);
            } catch (error) {
                console.error('Error fetching training data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [isAuthenticated, router]);

    const handleStartSession = async (questionId: number) => {
        setStartingSession(true);
        try {
            const session = await api.startTrainingSession(questionId);
            router.push(`/training/${session.id}`);
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
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Training Center</h1>
                    <p className="text-xl text-gray-600">Master your interview skills with instant AI feedback.</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Practice Questions */}
                    <div className="lg:col-span-2">
                        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                            <Mic className="w-6 h-6 mr-2 text-primary-600" />
                            Practice Questions
                        </h2>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <ul className="divide-y divide-gray-200">
                                {questions.map((question) => (
                                    <li key={question.id} className="p-6 hover:bg-gray-50 transition-colors">
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <h3 className="text-lg font-medium text-gray-900 mb-2">
                                                    {question.text}
                                                </h3>
                                                <div className="flex items-center space-x-2">
                                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                                                        {question.type.replace('_', ' ')}
                                                    </span>
                                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize
                                                        ${question.difficulty === 'hard' ? 'bg-red-100 text-red-800' :
                                                            question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                                                'bg-green-100 text-green-800'}`}>
                                                        {question.difficulty}
                                                    </span>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => handleStartSession(question.id)}
                                                disabled={startingSession}
                                                className="ml-4 flex items-center space-x-2 bg-primary-50 text-primary-700 px-4 py-2 rounded-lg hover:bg-primary-100 transition-colors font-medium"
                                            >
                                                <Play className="w-4 h-4" />
                                                <span>Practice</span>
                                            </button>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Recent Sessions */}
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                            <Clock className="w-6 h-6 mr-2 text-primary-600" />
                            Recent Sessions
                        </h2>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            {sessions.length > 0 ? (
                                <ul className="divide-y divide-gray-200">
                                    {sessions.map((session) => (
                                        <li key={session.id}>
                                            <Link href={`/training/${session.id}`} className="block hover:bg-gray-50 p-4">
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className={`px-2 py-0.5 rounded text-xs font-bold capitalize
                                                        ${session.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
                                                        {session.status}
                                                    </span>
                                                    <span className="text-xs text-gray-500">
                                                        {new Date(session.created_at).toLocaleDateString()}
                                                    </span>
                                                </div>
                                                <p className="text-sm font-medium text-gray-900 line-clamp-2 mb-2">
                                                    {session.question.text}
                                                </p>
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="p-8 text-center text-gray-500">
                                    No practice sessions yet.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
