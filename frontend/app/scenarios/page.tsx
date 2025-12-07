'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Scenario } from '@/types';
import { Loader2, Play, Briefcase, Coffee, Hotel, MessageSquare } from 'lucide-react';
import Navbar from '@/components/Navbar';

export default function ScenariosPage() {
    const router = useRouter();
    const [scenarios, setScenarios] = useState<Scenario[]>([]);
    const [loading, setLoading] = useState(true);
    const [startingScenario, setStartingScenario] = useState<number | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchScenarios();
    }, []);

    const fetchScenarios = async () => {
        try {
            const data = await api.getScenarios();
            setScenarios(data);
            setError(null);
        } catch (error) {
            console.error('Failed to fetch scenarios:', error);
            setError('Failed to load scenarios. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleStartScenario = async (scenario: Scenario) => {
        setStartingScenario(scenario.id);
        try {
            const session = await api.startConversation(undefined, scenario.id);
            router.push(`/conversation/${session.id}`);
        } catch (error) {
            console.error('Failed to start scenario:', error);
            setError('Failed to start scenario. Please try again.');
            setStartingScenario(null);
        }
    };

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'beginner':
                return 'bg-green-100 text-green-700 border-green-200';
            case 'intermediate':
                return 'bg-blue-100 text-blue-700 border-blue-200';
            case 'advanced':
                return 'bg-purple-100 text-purple-700 border-purple-200';
            default:
                return 'bg-gray-100 text-gray-700 border-gray-200';
        }
    };

    const getIcon = (iconName: string) => {
        const iconClass = "h-6 w-6";
        switch (iconName) {
            case 'briefcase':
                return <Briefcase className={iconClass} />;
            case 'coffee':
                return <Coffee className={iconClass} />;
            case 'hotel':
                return <Hotel className={iconClass} />;
            default:
                return <MessageSquare className={iconClass} />;
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
            <Navbar />

            {/* Header */}
            <div className="bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Practice Scenarios</h1>
                            <p className="text-sm text-gray-600 mt-1">
                                Choose a real-world scenario to practice your English skills
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {error && (
                    <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                        {error}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {scenarios.map((scenario) => (
                        <div
                            key={scenario.id}
                            className="bg-white/80 backdrop-blur-sm rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100"
                        >
                            {/* Card Header */}
                            <div className="p-6 pb-4">
                                <div className="flex justify-between items-start mb-3">
                                    <div className="p-3 bg-primary-50 rounded-lg text-primary-600">
                                        {getIcon(scenario.icon)}
                                    </div>
                                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getDifficultyColor(scenario.difficulty)}`}>
                                        {scenario.difficulty.charAt(0).toUpperCase() + scenario.difficulty.slice(1)}
                                    </span>
                                </div>
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                    {scenario.title}
                                </h3>
                                <p className="text-gray-600 text-sm">
                                    {scenario.description}
                                </p>
                            </div>

                            {/* Card Content */}
                            <div className="px-6 pb-4">
                                <h4 className="text-sm font-medium text-gray-700 mb-2">Objectives:</h4>
                                <ul className="space-y-1">
                                    {scenario.objectives.slice(0, 3).map((objective, index) => (
                                        <li key={index} className="text-sm text-gray-600 flex items-start">
                                            <span className="text-primary-500 mr-2">•</span>
                                            <span>{objective}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Card Footer */}
                            <div className="px-6 pb-6">
                                <button
                                    onClick={() => handleStartScenario(scenario)}
                                    disabled={startingScenario === scenario.id}
                                    className="w-full btn-primary py-3 px-4 text-sm font-medium flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {startingScenario === scenario.id ? (
                                        <>
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                            <span>Starting...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Play className="h-4 w-4" />
                                            <span>Start Practice</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {scenarios.length === 0 && !loading && !error && (
                    <div className="text-center py-12">
                        <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600">No scenarios available at the moment.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
