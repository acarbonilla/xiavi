'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { ArrowLeft, TrendingUp, Clock, MessageCircle, Flame } from 'lucide-react';
import Link from 'next/link';

export default function ProgressPage() {
    const { user } = useAuth();
    const profile = user?.learner_profile;

    const skills = profile?.skill_scores ? [
        { name: 'Clarity', score: profile.skill_scores.clarity, color: 'bg-blue-500' },
        { name: 'Fluency', score: profile.skill_scores.fluency, color: 'bg-purple-500' },
        { name: 'Vocabulary', score: profile.skill_scores.vocabulary, color: 'bg-green-500' },
        { name: 'Grammar', score: profile.skill_scores.grammar, color: 'bg-yellow-500' },
        { name: 'Confidence', score: profile.skill_scores.confidence, color: 'bg-orange-500' },
        { name: 'Engagement', score: profile.skill_scores.engagement, color: 'bg-red-500' },
    ] : [];

    const topicsCovered = profile?.topics_covered || {};
    const topTopics = Object.entries(topicsCovered)
        .sort(([, a], [, b]) => (b as number) - (a as number))
        .slice(0, 5);

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
                            <h1 className="text-xl font-bold text-gray-900">Your Progress</h1>
                            <p className="text-sm text-gray-600">Track your improvement</p>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
                {/* Stats Overview */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="card">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Conversations</p>
                                <p className="text-3xl font-bold text-gray-900">
                                    {profile?.total_conversations || 0}
                                </p>
                            </div>
                            <MessageCircle className="w-8 h-8 text-primary-600" />
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
                            <Clock className="w-8 h-8 text-purple-600" />
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
                            <Flame className="w-8 h-8 text-orange-600" />
                        </div>
                    </div>

                    <div className="card">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Longest Streak</p>
                                <p className="text-3xl font-bold text-gray-900">
                                    {profile?.longest_streak || 0}
                                </p>
                            </div>
                            <TrendingUp className="w-8 h-8 text-green-600" />
                        </div>
                    </div>
                </div>

                {/* Skill Scores */}
                <div className="card">
                    <h2 className="text-xl font-bold text-gray-900 mb-6">Current Skill Levels</h2>
                    {skills.length > 0 ? (
                        <div className="space-y-6">
                            {skills.map((skill) => (
                                <div key={skill.name}>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="font-medium text-gray-900">{skill.name}</span>
                                        <span className="text-2xl font-bold text-gray-900">
                                            {Math.round(skill.score)}
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-3">
                                        <div
                                            className={`h-3 rounded-full ${skill.color} transition-all duration-500`}
                                            style={{ width: `${skill.score}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-8">
                            Complete a conversation to see your skill scores
                        </p>
                    )}
                </div>

                {/* Topics Covered */}
                <div className="card">
                    <h2 className="text-xl font-bold text-gray-900 mb-6">Topics Practiced</h2>
                    {topTopics.length > 0 ? (
                        <div className="space-y-4">
                            {topTopics.map(([topic, count]) => (
                                <div key={topic} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                    <span className="font-medium text-gray-900">{topic}</span>
                                    <span className="badge bg-primary-100 text-primary-700">
                                        {count} {(count as number) === 1 ? 'conversation' : 'conversations'}
                                    </span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-8">
                            No topics practiced yet
                        </p>
                    )}
                </div>

                {/* Overall Progress */}
                <div className="card bg-gradient-to-br from-primary-500 to-purple-500 text-white">
                    <h2 className="text-2xl font-bold mb-4">Keep Going!</h2>
                    <p className="text-primary-100 mb-6">
                        {profile?.total_conversations === 0
                            ? "Start your first conversation to begin tracking your progress!"
                            : `You've completed ${profile?.total_conversations} conversations. Keep practicing to improve!`}
                    </p>
                    <Link href="/dashboard" className="btn-primary bg-white text-primary-600 hover:bg-gray-100 inline-block">
                        Continue Learning
                    </Link>
                </div>
            </div>
        </div>
    );
}
