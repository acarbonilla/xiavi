'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { VocabularyItem } from '@/types';
import {
    BookOpen,
    Search,
    Filter,
    RotateCcw,
    Check,
    X,
    ChevronLeft,
    ChevronRight,
    Trophy,
    Brain,
    Volume2
} from 'lucide-react';
import Navbar from '@/components/Navbar';

export default function VocabularyPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [vocabulary, setVocabulary] = useState<VocabularyItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'list' | 'review'>('list');
    const [searchQuery, setSearchQuery] = useState('');
    const [filterMastery, setFilterMastery] = useState<number | null>(null);

    // Review Mode State
    const [reviewQueue, setReviewQueue] = useState<VocabularyItem[]>([]);
    const [currentCardIndex, setCurrentCardIndex] = useState(0);
    const [isFlipped, setIsFlipped] = useState(false);
    const [reviewComplete, setReviewComplete] = useState(false);
    const [sessionStats, setSessionStats] = useState({ correct: 0, incorrect: 0 });

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
            return;
        }

        if (user) {
            fetchVocabulary();
        }
    }, [user, authLoading, router]);

    const fetchVocabulary = async () => {
        try {
            setLoading(true);
            const data = await api.getVocabulary();
            setVocabulary(data);
        } catch (error) {
            console.error('Failed to fetch vocabulary:', error);
        } finally {
            setLoading(false);
        }
    };

    const startReview = () => {
        // Prioritize items with lower mastery level or older review dates
        const sorted = [...vocabulary].sort((a, b) => {
            // First sort by mastery level (ascending)
            if (a.mastery_level !== b.mastery_level) {
                return a.mastery_level - b.mastery_level;
            }
            // Then by last reviewed (oldest first)
            const dateA = a.last_reviewed_at ? new Date(a.last_reviewed_at).getTime() : 0;
            const dateB = b.last_reviewed_at ? new Date(b.last_reviewed_at).getTime() : 0;
            return dateA - dateB;
        });

        // Take top 10 items for review
        const queue = sorted.slice(0, 10);

        if (queue.length === 0) {
            alert("No vocabulary words to review yet! Complete some conversations to build your list.");
            return;
        }

        setReviewQueue(queue);
        setCurrentCardIndex(0);
        setIsFlipped(false);
        setReviewComplete(false);
        setSessionStats({ correct: 0, incorrect: 0 });
        setActiveTab('review');
    };

    const handleCardResult = async (correct: boolean) => {
        const currentItem = reviewQueue[currentCardIndex];

        // Optimistic update
        setSessionStats(prev => ({
            ...prev,
            [correct ? 'correct' : 'incorrect']: prev[correct ? 'correct' : 'incorrect'] + 1
        }));

        try {
            await api.updateVocabularyMastery(currentItem.id, correct);
            // Refresh list in background
            fetchVocabulary();
        } catch (error) {
            console.error('Failed to update mastery:', error);
        }

        if (currentCardIndex < reviewQueue.length - 1) {
            setIsFlipped(false);
            setTimeout(() => setCurrentCardIndex(prev => prev + 1), 300);
        } else {
            setReviewComplete(true);
        }
    };

    const playPronunciation = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        window.speechSynthesis.speak(utterance);
    };

    const getMasteryColor = (level: number) => {
        switch (level) {
            case 1: return 'bg-red-100 text-red-700 border-red-200';
            case 2: return 'bg-orange-100 text-orange-700 border-orange-200';
            case 3: return 'bg-yellow-100 text-yellow-700 border-yellow-200';
            case 4: return 'bg-green-100 text-green-700 border-green-200';
            case 5: return 'bg-emerald-100 text-emerald-700 border-emerald-200';
            default: return 'bg-gray-100 text-gray-700 border-gray-200';
        }
    };

    const filteredVocabulary = vocabulary.filter(item => {
        const matchesSearch = item.word.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.definition.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesFilter = filterMastery ? item.mastery_level === filterMastery : true;
        return matchesSearch && matchesFilter;
    });

    if (authLoading || loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />
            <div className="p-6">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                                <BookOpen className="w-8 h-8 text-indigo-600" />
                                Vocabulary Builder
                            </h1>
                            <p className="text-gray-600 mt-1">
                                Master new words from your conversations
                            </p>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={() => setActiveTab('list')}
                                className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'list'
                                    ? 'bg-white text-indigo-600 shadow-sm border border-gray-200'
                                    : 'text-gray-600 hover:bg-white/50'
                                    }`}
                            >
                                Word List
                            </button>
                            <button
                                onClick={startReview}
                                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${activeTab === 'review'
                                    ? 'bg-indigo-600 text-white shadow-md'
                                    : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
                                    }`}
                            >
                                <RotateCcw className="w-4 h-4" />
                                Review Flashcards
                            </button>
                        </div>
                    </div>

                    {/* Content */}
                    {activeTab === 'list' ? (
                        <div className="space-y-6">
                            {/* Filters */}
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col md:flex-row gap-4">
                                <div className="relative flex-1">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        type="text"
                                        placeholder="Search words or definitions..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                                    />
                                </div>
                                <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0">
                                    <Filter className="w-5 h-5 text-gray-400" />
                                    {[1, 2, 3, 4, 5].map(level => (
                                        <button
                                            key={level}
                                            onClick={() => setFilterMastery(filterMastery === level ? null : level)}
                                            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors whitespace-nowrap ${filterMastery === level
                                                ? 'bg-indigo-100 text-indigo-700 border-indigo-200'
                                                : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                                                }`}
                                        >
                                            Level {level}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Word Grid */}
                            {filteredVocabulary.length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {filteredVocabulary.map((item) => (
                                        <div key={item.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow group">
                                            <div className="flex justify-between items-start mb-3">
                                                <h3 className="text-xl font-bold text-gray-900">{item.word}</h3>
                                                <span className={`px-2 py-1 rounded-md text-xs font-semibold border ${getMasteryColor(item.mastery_level)}`}>
                                                    Lvl {item.mastery_level}
                                                </span>
                                            </div>

                                            <p className="text-gray-600 mb-4 line-clamp-2" title={item.definition}>
                                                {item.definition}
                                            </p>

                                            {item.example_sentence && (
                                                <div className="bg-gray-50 p-3 rounded-lg mb-4">
                                                    <p className="text-sm text-gray-500 italic">"{item.example_sentence}"</p>
                                                </div>
                                            )}

                                            <div className="flex items-center justify-between mt-auto pt-4 border-t border-gray-50">
                                                <div className="text-xs text-gray-400">
                                                    Reviewed: {item.review_count} times
                                                </div>
                                                <button
                                                    onClick={() => playPronunciation(item.word)}
                                                    className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors"
                                                >
                                                    <Volume2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-12 bg-white rounded-xl border border-gray-100 border-dashed">
                                    <div className="bg-indigo-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <BookOpen className="w-8 h-8 text-indigo-600" />
                                    </div>
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">No words found</h3>
                                    <p className="text-gray-500 max-w-md mx-auto">
                                        {searchQuery || filterMastery
                                            ? "Try adjusting your search or filters."
                                            : "Start a conversation to discover new vocabulary words!"}
                                    </p>
                                </div>
                            )}
                        </div>
                    ) : (
                        /* Review Mode */
                        <div className="max-w-2xl mx-auto">
                            {!reviewComplete ? (
                                <div className="space-y-6">
                                    {/* Progress Bar */}
                                    <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                                        <span>Card {currentCardIndex + 1} of {reviewQueue.length}</span>
                                        <span>{Math.round(((currentCardIndex) / reviewQueue.length) * 100)}% Complete</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                                            style={{ width: `${((currentCardIndex) / reviewQueue.length) * 100}%` }}
                                        ></div>
                                    </div>

                                    {/* Flashcard */}
                                    <div
                                        className="relative h-96 w-full perspective-1000 cursor-pointer group"
                                        onClick={() => setIsFlipped(!isFlipped)}
                                    >
                                        <div className={`relative w-full h-full transition-transform duration-500 transform-style-3d ${isFlipped ? 'rotate-y-180' : ''}`}>
                                            {/* Front */}
                                            <div className="absolute w-full h-full backface-hidden bg-white rounded-2xl shadow-lg border border-gray-100 flex flex-col items-center justify-center p-8">
                                                <span className="text-sm font-medium text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full mb-6">
                                                    Word
                                                </span>
                                                <h2 className="text-4xl font-bold text-gray-900 mb-8 text-center">
                                                    {reviewQueue[currentCardIndex]?.word}
                                                </h2>
                                                <p className="text-gray-400 text-sm mt-auto">Click to flip</p>
                                            </div>

                                            {/* Back */}
                                            <div className="absolute w-full h-full backface-hidden rotate-y-180 bg-indigo-600 rounded-2xl shadow-lg flex flex-col items-center justify-center p-8 text-white">
                                                <span className="text-sm font-medium text-white/80 bg-white/20 px-3 py-1 rounded-full mb-6">
                                                    Definition
                                                </span>
                                                <p className="text-xl text-center font-medium mb-6 leading-relaxed">
                                                    {reviewQueue[currentCardIndex]?.definition}
                                                </p>
                                                {reviewQueue[currentCardIndex]?.example_sentence && (
                                                    <div className="bg-white/10 p-4 rounded-xl w-full">
                                                        <p className="text-sm text-white/90 italic text-center">
                                                            "{reviewQueue[currentCardIndex]?.example_sentence}"
                                                        </p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Controls */}
                                    {isFlipped && (
                                        <div className="flex gap-4 justify-center animate-in fade-in slide-in-from-bottom-4 duration-300">
                                            <button
                                                onClick={(e) => { e.stopPropagation(); handleCardResult(false); }}
                                                className="flex-1 bg-white border-2 border-red-100 text-red-600 py-3 px-6 rounded-xl font-semibold hover:bg-red-50 hover:border-red-200 transition-colors flex items-center justify-center gap-2"
                                            >
                                                <X className="w-5 h-5" />
                                                Still Learning
                                            </button>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); handleCardResult(true); }}
                                                className="flex-1 bg-indigo-600 text-white py-3 px-6 rounded-xl font-semibold hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all flex items-center justify-center gap-2"
                                            >
                                                <Check className="w-5 h-5" />
                                                Got It!
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                /* Review Complete */
                                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-12 text-center animate-in zoom-in duration-300">
                                    <div className="bg-yellow-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                                        <Trophy className="w-10 h-10 text-yellow-600" />
                                    </div>
                                    <h2 className="text-3xl font-bold text-gray-900 mb-2">Session Complete!</h2>
                                    <p className="text-gray-600 mb-8">Great job reviewing your vocabulary.</p>

                                    <div className="grid grid-cols-2 gap-4 max-w-xs mx-auto mb-8">
                                        <div className="bg-green-50 p-4 rounded-xl border border-green-100">
                                            <div className="text-2xl font-bold text-green-600">{sessionStats.correct}</div>
                                            <div className="text-sm text-green-700">Correct</div>
                                        </div>
                                        <div className="bg-red-50 p-4 rounded-xl border border-red-100">
                                            <div className="text-2xl font-bold text-red-600">{sessionStats.incorrect}</div>
                                            <div className="text-sm text-red-700">Learning</div>
                                        </div>
                                    </div>

                                    <div className="flex gap-3 justify-center">
                                        <button
                                            onClick={() => setActiveTab('list')}
                                            className="px-6 py-2 text-gray-600 hover:bg-gray-50 rounded-lg font-medium transition-colors"
                                        >
                                            Back to List
                                        </button>
                                        <button
                                            onClick={startReview}
                                            className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 shadow-md transition-all"
                                        >
                                            Review More
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <style jsx global>{`
                .perspective-1000 { perspective: 1000px; }
                .transform-style-3d { transform-style: preserve-3d; }
                .backface-hidden { backface-visibility: hidden; }
                .rotate-y-180 { transform: rotateY(180deg); }
            `}</style>
            </div>
        </div>
    );
}
