'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import Link from 'next/link';
import { MessageCircle, Mail, Lock, User, Phone, AlertCircle, CheckCircle } from 'lucide-react';

export default function RegisterPage() {
    const { register } = useAuth();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password2: '',
        first_name: '',
        last_name: '',
        language_level: 'beginner' as 'beginner' | 'intermediate' | 'advanced',
        native_language: 'English',
        target_language: 'English',
        phone: '',
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (formData.password !== formData.password2) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        try {
            await register(formData);
            setSuccess(true);
        } catch (err: any) {
            const errorData = err.response?.data;
            if (errorData) {
                const errorMessages = Object.entries(errorData)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(', ');
                setError(errorMessages);
            } else {
                setError('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-purple-50 flex items-center justify-center p-4">
                <div className="max-w-md w-full card text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-8 h-8 text-green-600" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to XiAv!</h2>
                    <p className="text-gray-600 mb-6">
                        Your account has been created. Start improving your speech skills now!
                    </p>
                    <Link href="/login" className="btn-primary inline-block">
                        Go to Login
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-purple-50 flex items-center justify-center p-4 py-12">
            <div className="max-w-2xl w-full">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center space-x-2 mb-2">
                        <MessageCircle className="w-10 h-10 text-primary-600" />
                        <span className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
                            XiAv Speech AI
                        </span>
                    </div>
                    <p className="text-gray-600">Start your speaking journey</p>
                </div>

                {/* Register Form */}
                <div className="card">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {error && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
                                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                                <p className="text-sm text-red-800">{error}</p>
                            </div>
                        )}

                        {/* Language Level Selection */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Your Level
                            </label>
                            <div className="grid grid-cols-3 gap-4">
                                {(['beginner', 'intermediate', 'advanced'] as const).map((level) => (
                                    <button
                                        key={level}
                                        type="button"
                                        onClick={() => setFormData({ ...formData, language_level: level })}
                                        className={`p-4 border-2 rounded-lg transition-all capitalize ${formData.language_level === level
                                                ? 'border-primary-600 bg-primary-50'
                                                : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        <p className="font-semibold">{level}</p>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Name Fields */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
                                    First Name
                                </label>
                                <input
                                    id="first_name"
                                    type="text"
                                    required
                                    className="input-field"
                                    value={formData.first_name}
                                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                />
                            </div>
                            <div>
                                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
                                    Last Name
                                </label>
                                <input
                                    id="last_name"
                                    type="text"
                                    required
                                    className="input-field"
                                    value={formData.last_name}
                                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                />
                            </div>
                        </div>

                        {/* Username & Email */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                                    Username
                                </label>
                                <input
                                    id="username"
                                    type="text"
                                    required
                                    className="input-field"
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                />
                            </div>
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                    Email
                                </label>
                                <input
                                    id="email"
                                    type="email"
                                    required
                                    className="input-field"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>
                        </div>

                        {/* Password Fields */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                                    Password
                                </label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        id="password"
                                        type="password"
                                        required
                                        className="input-field pl-10"
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div>
                                <label htmlFor="password2" className="block text-sm font-medium text-gray-700 mb-2">
                                    Confirm Password
                                </label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <input
                                        id="password2"
                                        type="password"
                                        required
                                        className="input-field pl-10"
                                        value={formData.password2}
                                        onChange={(e) => setFormData({ ...formData, password2: e.target.value })}
                                    />
                                </div>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Creating Account...' : 'Create Account'}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-gray-600">
                            Already have an account?{' '}
                            <Link href="/login" className="text-primary-600 hover:text-primary-700 font-semibold">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </div>

                <div className="mt-6 text-center">
                    <Link href="/" className="text-gray-600 hover:text-gray-900 text-sm">
                        ← Back to home
                    </Link>
                </div>
            </div>
        </div>
    );
}
