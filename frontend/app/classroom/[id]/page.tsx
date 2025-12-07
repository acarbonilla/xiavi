'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { Send, User as UserIcon, Bot, ArrowLeft, CheckCircle, AlertCircle, BookOpen } from 'lucide-react';
import Link from 'next/link';

export default function ClassroomSessionPage() {
    const { id } = useParams();
    const { user, isAuthenticated, loading: authLoading } = useAuth();
    const router = useRouter();
    const [session, setSession] = useState<any>(null);
    const [messages, setMessages] = useState<any[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [sending, setSending] = useState(false);
    const [loading, setLoading] = useState(true);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (authLoading) return;

        if (!isAuthenticated) {
            router.push('/login');
            return;
        }

        const fetchSession = async () => {
            try {
                const sessionData = await api.getClassroomSession(Number(id));
                setSession(sessionData);
                setMessages(sessionData.messages || []);
            } catch (error) {
                console.error('Error fetching session:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchSession();
    }, [id, isAuthenticated, authLoading, router]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newMessage.trim() || sending) return;

        const messageText = newMessage;
        setNewMessage('');
        setSending(true);

        // Optimistically add user message
        const tempMessage = {
            id: Date.now(),
            role: 'user',
            text: messageText,
            created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, tempMessage]);

        try {
            const response = await api.sendClassroomMessage(Number(id), messageText);
            // Add AI response
            setMessages(prev => [...prev, response]);
        } catch (error) {
            console.error('Error sending message:', error);
            // TODO: Show error toast
        } finally {
            setSending(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    if (!session) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-gray-900">Session not found</h2>
                    <Link href="/classroom" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
                        Return to Classroom
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Header */}
            <header className="bg-white shadow-sm z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center">
                        <Link href="/classroom" className="mr-4 text-gray-500 hover:text-gray-700">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">
                                {session.topic?.name || 'General Class'}
                            </h1>
                            <p className="text-xs text-gray-500">AI Teacher Session</p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Chat Area */}
            <main className="flex-1 overflow-y-auto p-4 sm:p-6">
                <div className="max-w-3xl mx-auto space-y-6">
                    {messages.map((msg, index) => (
                        <div key={msg.id || index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`flex max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                {/* Avatar */}
                                <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-primary-100 ml-3' : 'bg-green-100 mr-3'
                                    }`}>
                                    {msg.role === 'user' ? (
                                        <UserIcon className="w-6 h-6 text-primary-600" />
                                    ) : (
                                        <Bot className="w-6 h-6 text-green-600" />
                                    )}
                                </div>

                                {/* Message Bubble */}
                                <div>
                                    <div className={`rounded-2xl px-5 py-3 shadow-sm ${msg.role === 'user'
                                        ? 'bg-primary-600 text-white rounded-tr-none'
                                        : 'bg-white text-gray-900 rounded-tl-none border border-gray-100'
                                        }`}>
                                        <p className="whitespace-pre-wrap">{msg.text}</p>
                                    </div>

                                    {/* Correction / Explanation (Only for AI messages) */}
                                    {msg.role === 'ai' && (msg.correction || msg.explanation) && (
                                        <div className="mt-2 bg-yellow-50 border border-yellow-100 rounded-xl p-3 text-sm">
                                            {msg.correction && (
                                                <div className="flex items-start mb-2">
                                                    <AlertCircle className="w-4 h-4 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                                                    <div>
                                                        <span className="font-semibold text-yellow-800">Correction: </span>
                                                        <span className="text-yellow-900">{msg.correction}</span>
                                                    </div>
                                                </div>
                                            )}
                                            {msg.explanation && (
                                                <div className="flex items-start">
                                                    <BookOpen className="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                                                    <div>
                                                        <span className="font-semibold text-blue-800">Teacher's Note: </span>
                                                        <span className="text-blue-900">{msg.explanation}</span>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>
            </main>

            {/* Input Area */}
            <div className="bg-white border-t border-gray-200 p-4">
                <div className="max-w-3xl mx-auto">
                    <form onSubmit={handleSendMessage} className="flex items-center space-x-4">
                        <input
                            type="text"
                            value={newMessage}
                            onChange={(e) => setNewMessage(e.target.value)}
                            placeholder="Type your message..."
                            className="flex-1 rounded-full border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 py-3 px-6"
                            disabled={sending}
                        />
                        <button
                            type="submit"
                            disabled={!newMessage.trim() || sending}
                            className="bg-primary-600 text-white p-3 rounded-full hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
