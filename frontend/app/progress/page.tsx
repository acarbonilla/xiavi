'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import { ArrowLeft, TrendingUp, Calendar, Clock, BarChart3 } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ProgressPage() {
    const [analytics, setAnalytics] = useState<any>(null);
    const [days, setDays] = useState(30);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAnalytics();
    }, [days]);

    const fetchAnalytics = async () => {
        try {
            const data = await api.getAnalytics(days);
            setAnalytics(data);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    const hasData = analytics && analytics.skill_progress && analytics.skill_progress.length > 0;

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-4 py-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Progress Dashboard</h1>
                            <p className="text-sm text-gray-600">Track your improvement over time</p>
                        </div>
                    </div>
                    <div className="flex space-x-2">
                        {[7, 30, 90].map((d) => (
                            <button
                                key={d}
                                onClick={() => setDays(d)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${days === d
                                        ? 'bg-primary-600 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                {d} Days
                            </button>
                        ))}
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 py-8">
                {!hasData ? (
                    <div className="card text-center py-12">
                        <div className="text-6xl mb-4">📊</div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Data Yet</h2>
                        <p className="text-gray-600 mb-6">
                            Complete some conversations to see your progress!
                        </p>
                        <Link href="/dashboard" className="btn-primary inline-block">
                            Start Practicing
                        </Link>
                    </div>
                ) : (
                    <div className="space-y-8">
                        {/* Summary Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="card">
                                <div className="flex items-center space-x-3">
                                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <BarChart3 className="w-6 h-6 text-blue-600" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-600">Total Conversations</p>
                                        <p className="text-2xl font-bold text-gray-900">
                                            {analytics.total_conversations}
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div className="card">
                                <div className="flex items-center space-x-3">
                                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                                        <TrendingUp className="w-6 h-6 text-green-600" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-600">Avg. Score</p>
                                        <p className="text-2xl font-bold text-gray-900">
                                            {analytics.skill_progress.length > 0
                                                ? Math.round(
                                                    analytics.skill_progress.reduce(
                                                        (sum: number, d: any) => sum + d.overall,
                                                        0
                                                    ) / analytics.skill_progress.length
                                                )
                                                : 0}
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div className="card">
                                <div className="flex items-center space-x-3">
                                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                                        <Clock className="w-6 h-6 text-purple-600" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-600">Total Speaking Time</p>
                                        <p className="text-2xl font-bold text-gray-900">
                                            {Math.round(
                                                analytics.speaking_time.reduce(
                                                    (sum: number, d: any) => sum + d.minutes,
                                                    0
                                                )
                                            )}
                                            m
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Skill Progress Chart */}
                        <div className="card">
                            <div className="flex items-center space-x-2 mb-6">
                                <TrendingUp className="w-5 h-5 text-primary-600" />
                                <h2 className="text-xl font-semibold text-gray-900">Skill Progress Over Time</h2>
                            </div>
                            <ResponsiveContainer width="100%" height={400}>
                                <LineChart data={analytics.skill_progress}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis domain={[0, 100]} />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="overall" stroke="#3b82f6" strokeWidth={2} name="Overall" />
                                    <Line type="monotone" dataKey="clarity" stroke="#8b5cf6" name="Clarity" />
                                    <Line type="monotone" dataKey="fluency" stroke="#10b981" name="Fluency" />
                                    <Line type="monotone" dataKey="vocabulary" stroke="#f59e0b" name="Vocabulary" />
                                    <Line type="monotone" dataKey="grammar" stroke="#ef4444" name="Grammar" />
                                    <Line type="monotone" dataKey="confidence" stroke="#ec4899" name="Confidence" />
                                    <Line type="monotone" dataKey="engagement" stroke="#06b6d4" name="Engagement" />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Speaking Time Chart */}
                        <div className="card">
                            <div className="flex items-center space-x-2 mb-6">
                                <Clock className="w-5 h-5 text-primary-600" />
                                <h2 className="text-xl font-semibold text-gray-900">Speaking Time by Week</h2>
                            </div>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={analytics.speaking_time}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="week_start" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="minutes" fill="#3b82f6" name="Speaking Minutes" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Activity Heatmap */}
                        <div className="card">
                            <div className="flex items-center space-x-2 mb-6">
                                <Calendar className="w-5 h-5 text-primary-600" />
                                <h2 className="text-xl font-semibold text-gray-900">Practice Activity</h2>
                            </div>
                            <div className="grid grid-cols-7 gap-2">
                                {analytics.speaking_time.map((week: any, idx: number) => (
                                    <div key={idx} className="text-center">
                                        <div
                                            className={`h-20 rounded-lg flex items-center justify-center transition-colors ${week.conversations === 0
                                                    ? 'bg-gray-100'
                                                    : week.conversations >= 5
                                                        ? 'bg-green-500 text-white'
                                                        : week.conversations >= 3
                                                            ? 'bg-green-400 text-white'
                                                            : 'bg-green-200'
                                                }`}
                                        >
                                            <div>
                                                <div className="text-2xl font-bold">{week.conversations}</div>
                                                <div className="text-xs">conversations</div>
                                            </div>
                                        </div>
                                        <div className="text-xs text-gray-600 mt-1">
                                            {new Date(week.week_start).toLocaleDateString('en-US', {
                                                month: 'short',
                                                day: 'numeric',
                                            })}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
