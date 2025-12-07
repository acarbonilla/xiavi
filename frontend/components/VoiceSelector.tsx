'use client';

import { useState } from 'react';
import { Voice } from '@/types';
import { Mic, Volume2, Check } from 'lucide-react';

interface VoiceSelectorProps {
    voices: Voice[];
    selectedVoice?: string;
    onVoiceChange: (voiceId: string) => void;
    showPreview?: boolean;
    onPreview?: (voiceId: string) => void;
}

export default function VoiceSelector({
    voices,
    selectedVoice,
    onVoiceChange,
    showPreview = true,
    onPreview,
}: VoiceSelectorProps) {
    const [previewingVoice, setPreviewingVoice] = useState<string | null>(null);

    const handlePreview = async (voiceId: string) => {
        if (!onPreview) return;

        setPreviewingVoice(voiceId);
        try {
            await onPreview(voiceId);
        } finally {
            setPreviewingVoice(null);
        }
    };

    const getVoiceIcon = (gender: string) => {
        return gender === 'male' ? '👨' : '👩';
    };

    const getVoiceColor = (tone: string) => {
        const colors: Record<string, string> = {
            energetic: 'from-orange-500 to-pink-500',
            conversational: 'from-blue-500 to-purple-500',
            authoritative: 'from-gray-600 to-gray-800',
            gentle: 'from-green-400 to-teal-500',
        };
        return colors[tone] || 'from-blue-500 to-purple-500';
    };

    return (
        <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Select AI Voice
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {voices.map((voice) => {
                    const isSelected = selectedVoice === voice.id;
                    const isPreviewing = previewingVoice === voice.id;

                    return (
                        <button
                            key={voice.id}
                            type="button"
                            onClick={() => onVoiceChange(voice.id)}
                            className={`
                relative p-4 rounded-lg border-2 transition-all duration-200
                ${isSelected
                                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                    : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
                                }
                ${isPreviewing ? 'ring-2 ring-blue-400' : ''}
              `}
                        >
                            {/* Selected indicator */}
                            {isSelected && (
                                <div className="absolute top-2 right-2">
                                    <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                                        <Check className="w-4 h-4 text-white" />
                                    </div>
                                </div>
                            )}

                            {/* Voice info */}
                            <div className="flex items-start gap-3">
                                {/* Icon with gradient */}
                                <div className={`
                  w-12 h-12 rounded-full bg-gradient-to-br ${getVoiceColor(voice.tone)}
                  flex items-center justify-center text-2xl
                `}>
                                    {getVoiceIcon(voice.gender)}
                                </div>

                                <div className="flex-1 text-left">
                                    <h3 className="font-semibold text-gray-900 dark:text-white">
                                        {voice.name}
                                    </h3>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                        {voice.description}
                                    </p>
                                    <div className="flex items-center gap-2 mt-2">
                                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                                            {voice.gender}
                                        </span>
                                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                                            {voice.tone}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Preview button */}
                            {showPreview && onPreview && (
                                <button
                                    type="button"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handlePreview(voice.id);
                                    }}
                                    disabled={isPreviewing}
                                    className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 rounded-md hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isPreviewing ? (
                                        <>
                                            <Volume2 className="w-4 h-4 animate-pulse" />
                                            <span>Playing...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Volume2 className="w-4 h-4" />
                                            <span>Preview Voice</span>
                                        </>
                                    )}
                                </button>
                            )}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
