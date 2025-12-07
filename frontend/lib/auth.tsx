'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginRequest, RegisterRequest } from '@/types';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (data: LoginRequest) => Promise<void>;
    register: (data: RegisterRequest) => Promise<void>;
    logout: () => Promise<void>;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        // Load user from localStorage on mount
        const loadUser = async () => {
            if (typeof window !== 'undefined') {
                const storedUser = localStorage.getItem('user');
                const accessToken = localStorage.getItem('access_token');
                const refreshToken = localStorage.getItem('refresh_token');

                if (storedUser && (accessToken || refreshToken)) {
                    try {
                        setUser(JSON.parse(storedUser));

                        // Validate token by fetching user profile
                        try {
                            const profile = await api.getProfile();
                            setUser(profile);
                            localStorage.setItem('user', JSON.stringify(profile));
                        } catch (error) {
                            // Token might be expired, try refresh
                            console.log('Token validation failed, may need to re-login');
                        }
                    } catch (error) {
                        console.error('Error parsing stored user:', error);
                        localStorage.removeItem('user');
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('refresh_token');
                    }
                }
            }
            setLoading(false);
        };

        loadUser();
    }, []);

    const login = async (data: LoginRequest) => {
        try {
            const response = await api.login(data);
            setUser(response.user);
            router.push('/dashboard');
        } catch (error) {
            throw error;
        }
    };



    const register = async (data: RegisterRequest) => {
        try {
            await api.register(data);
            // After registration, redirect to login
            router.push('/login');
        } catch (error) {
            throw error;
        }
    };

    const logout = async () => {
        try {
            await api.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            setUser(null);
            router.push('/login');
        }
    };

    const value: AuthContextType = {
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
