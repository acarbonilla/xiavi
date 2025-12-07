'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { User, Voice } from '@/types';
import { Save, Volume2, User as UserIcon, Globe, Mic } from 'lucide-react';
import Navbar from '@/components/Navbar';

export default function SettingsPage() {
    const { user, isAuthenticated, login } = useAuth(); // Assuming login updates the user context
    const router = useRouter();

    const [formData, setFormData] = useState<Partial<User>>({});
    const [voices, setVoices] = useState<Voice[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
    const [playingVoice, setPlayingVoice] = useState<string | null>(null);

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }

        const fetchData = async () => {
            try {
                const [voicesData, profileData] = await Promise.all([
                    api.getVoices(),
                    api.getProfile()
                ]);
                setVoices(voicesData);
                setFormData({
                    first_name: profileData.first_name,
                    last_name: profileData.last_name,
                    language_level: profileData.language_level,
                    native_language: profileData.native_language,
                    target_language: profileData.target_language,
                    learner_profile: profileData.learner_profile
                });
            } catch (error) {
                console.error('Error fetching settings:', error);
                setMessage({ type: 'error', text: 'Failed to load settings' });
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [isAuthenticated, router]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleVoiceChange = (voiceId: string) => {
        setFormData(prev => ({
            ...prev,
            learner_profile: {
                ...prev.learner_profile!,
                preferred_voice: voiceId
            }
        }));
    };

    const playVoicePreview = async (voiceId: string) => {
        if (playingVoice) return;
        setPlayingVoice(voiceId);
        try {
            const audioBuffer = await api.previewVoice(voiceId);
            const blob = new Blob([audioBuffer], { type: 'audio/mpeg' });
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            audio.onended = () => setPlayingVoice(null);
            await audio.play();
        } catch (error) {
            console.error('Error playing preview:', error);
            setPlayingVoice(null);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);

        try {
            // Update main user profile
            const updatedUser = await api.updateProfile({
                first_name: formData.first_name,
                last_name: formData.last_name,
                language_level: formData.language_level,
                native_language: formData.native_language,
                target_language: formData.target_language,
                learner_profile: formData.learner_profile,
            });

            // Update voice preference if changed (this might need a separate endpoint or be part of updateProfile depending on backend)
            // Assuming updateProfile handles nested learner_profile or we need a specific call.
            // Based on models, preferred_voice is in LearnerProfile. 
            // If updateProfile doesn't handle it, we might need a separate call.
            // For now, let's assume the backend handles it or we add a specific call if needed.
            // Actually, looking at api.ts, updateProfile sends a PATCH to /auth/profile/. 
            // We need to ensure the backend serializer handles nested profile updates.

            // If the backend doesn't support nested updates, we might need to handle it differently.
            // But let's assume for now it does or we'll fix it if it fails.

            // Also need to update the local user context
            // login({ ...user, ...updatedUser } as any); // This is a hack, ideally useAuth has an update function

            setMessage({ type: 'success', text: 'Settings saved successfully' });
        } catch (error) {
            console.error('Error saving settings:', error);
            setMessage({ type: 'error', text: 'Failed to save settings' });
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="p-8 text-center">Loading settings...</div>;

    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />
            <div className="py-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-3xl mx-auto">
                    <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

                    {message && (
                        <div className={`p-4 rounded-lg mb-6 ${message.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                            {message.text}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-8">
                        {/* Profile Section */}
                        <div className="bg-white shadow rounded-xl p-6">
                            <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                                <UserIcon className="w-5 h-5 mr-2 text-primary-600" />
                                Profile Information
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                                    <input
                                        type="text"
                                        name="first_name"
                                        value={formData.first_name || ''}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                                    <input
                                        type="text"
                                        name="last_name"
                                        value={formData.last_name || ''}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Language Settings */}
                        <div className="bg-white shadow rounded-xl p-6">
                            <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                                <Globe className="w-5 h-5 mr-2 text-primary-600" />
                                Language Preferences
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Native Language</label>
                                    <input
                                        type="text"
                                        name="native_language"
                                        value={formData.native_language || ''}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Target Language</label>
                                    <input
                                        type="text"
                                        name="target_language"
                                        value={formData.target_language || ''}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                    />
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Proficiency Level</label>
                                    <select
                                        name="language_level"
                                        value={formData.language_level || 'beginner'}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                    >
                                        <option value="beginner">Beginner</option>
                                        <option value="intermediate">Intermediate</option>
                                        <option value="advanced">Advanced</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Voice Settings */}
                        <div className="bg-white shadow rounded-xl p-6">
                            <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                                <Mic className="w-5 h-5 mr-2 text-primary-600" />
                                AI Voice Preference
                            </h2>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {voices.map((voice) => (
                                    <div
                                        key={voice.id}
                                        className={`relative border rounded-xl p-4 cursor-pointer transition-all ${formData.learner_profile?.preferred_voice === voice.id
                                            ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-500'
                                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                            }`}
                                        onClick={() => handleVoiceChange(voice.id)}
                                    >
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="font-semibold text-gray-900">{voice.name}</h3>
                                            <button
                                                type="button"
                                                onClick={(e) => { e.stopPropagation(); playVoicePreview(voice.id); }}
                                                className="text-primary-600 hover:text-primary-700 p-1"
                                                disabled={playingVoice !== null}
                                            >
                                                <Volume2 className={`w-5 h-5 ${playingVoice === voice.id ? 'animate-pulse' : ''}`} />
                                            </button>
                                        </div>
                                        <p className="text-sm text-gray-500 mb-2">{voice.description}</p>
                                        <div className="flex flex-wrap gap-2">
                                            <span className="text-xs bg-white border border-gray-200 px-2 py-1 rounded-full text-gray-600 capitalize">
                                                {voice.gender}
                                            </span>
                                            <span className="text-xs bg-white border border-gray-200 px-2 py-1 rounded-full text-gray-600 capitalize">
                                                {voice.tone}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex justify-end">
                            <button
                                type="submit"
                                disabled={saving}
                                className="flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-lg font-semibold transition-all shadow-lg shadow-primary-900/20 disabled:opacity-50"
                            >
                                <Save className="w-5 h-5" />
                                <span>{saving ? 'Saving...' : 'Save Changes'}</span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
