'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';

interface GoalProgress {
    conversations_today: number;
    speaking_minutes_today: number;
    goal_conversations: number;
    goal_minutes: number;
    conversations_progress: number;
    minutes_progress: number;
    goals_met: boolean;
    current_streak: number;
    longest_streak: number;
}

export default function GoalWidget() {
    const [progress, setProgress] = useState<GoalProgress | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchProgress();
    }, []);

    const fetchProgress = async () => {
        try {
            const data = await api.getGoalStatus();
            setProgress(data);
        } catch (error) {
            console.error('Error fetching goal status:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading || !progress) {
        return (
            <div className="card animate-pulse">
                <div className="h-32 bg-gray-200 rounded"></div>
            </div>
        );
    }

    const overallProgress = Math.min(100, (progress.conversations_progress + progress.minutes_progress) / 2);

    return (
        <div className="card">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Daily Goals</h3>
                {progress.current_streak > 0 && (
                    <div className="flex items-center space-x-2">
                        <span className="text-2xl">🔥</span>
                        <div className="text-right">
                            <div className="text-2xl font-bold text-orange-600">{progress.current_streak}</div>
                            <div className="text-xs text-gray-600">day streak</div>
                        </div>
                    </div>
                )}
            </div>

            {/* Circular Progress */}
            <div className="flex justify-center mb-6">
                <div className="relative w-32 h-32">
                    <svg className="w-full h-full transform -rotate-90">
                        <circle
                            cx="64"
                            cy="64"
                            r="56"
                            stroke="currentColor"
                            strokeWidth="8"
                            fill="none"
                            className="text-gray-200"
                        />
                        <circle
                            cx="64"
                            cy="64"
                            r="56"
                            stroke="currentColor"
                            strokeWidth="8"
                            fill="none"
                            strokeDasharray={`${2 * Math.PI * 56}`}
                            strokeDashoffset={`${2 * Math.PI * 56 * (1 - overallProgress / 100)}`}
                            className={`transition-all duration-500 ${progress.goals_met ? 'text-green-500' : 'text-primary-600'
                                }`}
                            strokeLinecap="round"
                        />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                            <div className="text-3xl font-bold text-gray-900">
                                {Math.round(overallProgress)}%
                            </div>
                            {progress.goals_met && (
                                <div className="text-green-600 text-sm font-medium">✓ Complete!</div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Progress Details */}
            <div className="space-y-3">
                <div>
                    <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Conversations</span>
                        <span className="font-medium">
                            {progress.conversations_today}/{progress.goal_conversations}
                        </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                            className={`h-2 rounded-full transition-all duration-500 ${progress.conversations_today >= progress.goal_conversations
                                    ? 'bg-green-500'
                                    : 'bg-primary-600'
                                }`}
                            style={{ width: `${Math.min(100, progress.conversations_progress)}%` }}
                        ></div>
                    </div>
                </div>

                <div>
                    <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Speaking Time</span>
                        <span className="font-medium">
                            {progress.speaking_minutes_today.toFixed(1)}/{progress.goal_minutes} min
                        </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                            className={`h-2 rounded-full transition-all duration-500 ${progress.speaking_minutes_today >= progress.goal_minutes
                                    ? 'bg-green-500'
                                    : 'bg-primary-600'
                                }`}
                            style={{ width: `${Math.min(100, progress.minutes_progress)}%` }}
                        ></div>
                    </div>
                </div>
            </div>

            {/* Motivational Message */}
            <div className="mt-4 text-center">
                {progress.goals_met ? (
                    <p className="text-green-600 font-medium">🎉 Amazing work today!</p>
                ) : (
                    <p className="text-gray-600 text-sm">
                        {overallProgress > 50 ? "You're doing great! Keep going!" : "Let's practice today!"}
                    </p>
                )}
                {progress.current_streak >= 7 && (
                    <p className="text-orange-600 text-sm mt-1">
                        🏆 {progress.current_streak} day streak! Keep it up!
                    </p>
                )}
            </div>

            {/* Settings Link */}
            <Link
                href="/profile"
                className="mt-4 block text-center text-sm text-primary-600 hover:text-primary-700"
            >
                Adjust goals
            </Link>
        </div>
    );
}
