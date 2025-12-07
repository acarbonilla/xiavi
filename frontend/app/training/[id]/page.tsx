'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { Video, Mic, StopCircle, Play, RotateCcw, CheckCircle, AlertTriangle, Star, MessageSquare } from 'lucide-react';

export default function TrainingSessionPage() {
    const { id } = useParams();
    const router = useRouter();
    const { isAuthenticated } = useAuth();

    const [session, setSession] = useState<any>(null);
    const [isRecording, setIsRecording] = useState(false);
    const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
    const [videoUrl, setVideoUrl] = useState<string | null>(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [feedback, setFeedback] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }

        const fetchSession = async () => {
            try {
                const data = await api.getTrainingSession(Number(id));
                setSession(data);
                // If session already has feedback, load it (assuming backend returns it)
                if (data.feedbacks && data.feedbacks.length > 0) {
                    setFeedback(data.feedbacks[0]);
                    setVideoUrl(data.feedbacks[0].video_url); // Assuming backend provides URL
                }
            } catch (err) {
                console.error('Error fetching session:', err);
                setError('Failed to load training session');
            } finally {
                setLoading(false);
            }
        };

        fetchSession();

        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, [id, isAuthenticated, router]);

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            streamRef.current = stream;
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
        } catch (err) {
            console.error('Error accessing camera:', err);
            setError('Could not access camera/microphone. Please allow permissions.');
        }
    };

    const startRecording = () => {
        if (!streamRef.current) {
            startCamera().then(() => {
                if (streamRef.current) startRecording();
            });
            return;
        }

        const recorder = new MediaRecorder(streamRef.current);
        const chunks: Blob[] = [];

        recorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunks.push(e.data);
        };

        recorder.onstop = async () => {
            const blob = new Blob(chunks, { type: 'video/webm' });
            const url = URL.createObjectURL(blob);
            setVideoUrl(url);

            // Auto-submit for analysis
            await analyzeRecording(blob);
        };

        recorder.start();
        setMediaRecorder(recorder);
        setIsRecording(true);
        setFeedback(null);
    };

    const stopRecording = () => {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            setIsRecording(false);
        }
    };

    const analyzeRecording = async (blob: Blob) => {
        setAnalyzing(true);
        try {
            const data = await api.generateTrainingFeedback(Number(id), blob);
            setFeedback(data);
            await api.completeTrainingSession(Number(id));
        } catch (err) {
            console.error('Error analyzing recording:', err);
            setError('Failed to analyze recording. Please try again.');
        } finally {
            setAnalyzing(false);
        }
    };

    const handleRetake = () => {
        setVideoUrl(null);
        setFeedback(null);
        if (videoRef.current && streamRef.current) {
            videoRef.current.srcObject = streamRef.current;
        }
    };

    if (loading) return <div className="p-8 text-center">Loading session...</div>;
    if (error) return <div className="p-8 text-center text-red-600">{error}</div>;
    if (!session) return <div className="p-8 text-center">Session not found</div>;

    return (
        <div className="min-h-screen bg-gray-900 text-white p-4 sm:p-8">
            <div className="max-w-6xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left Column: Video & Controls */}
                    <div className="space-y-6">
                        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                            <h2 className="text-lg font-semibold text-gray-200 mb-2">Question</h2>
                            <p className="text-2xl font-medium text-white leading-relaxed">
                                {session.question.text}
                            </p>
                        </div>

                        <div className="relative aspect-video bg-black rounded-2xl overflow-hidden shadow-2xl border border-gray-800">
                            {videoUrl ? (
                                <video src={videoUrl} controls className="w-full h-full object-cover" />
                            ) : (
                                <video ref={videoRef} autoPlay muted playsInline className="w-full h-full object-cover" />
                            )}

                            {isRecording && (
                                <div className="absolute top-4 right-4 flex items-center space-x-2 bg-red-600/90 text-white px-3 py-1 rounded-full animate-pulse">
                                    <div className="w-2 h-2 bg-white rounded-full"></div>
                                    <span className="text-xs font-bold uppercase">Recording</span>
                                </div>
                            )}
                        </div>

                        <div className="flex justify-center space-x-4">
                            {!isRecording && !videoUrl && (
                                <button
                                    onClick={startRecording}
                                    className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white px-8 py-4 rounded-full font-bold transition-all transform hover:scale-105"
                                >
                                    <div className="w-4 h-4 bg-white rounded-full"></div>
                                    <span>Start Recording</span>
                                </button>
                            )}

                            {isRecording && (
                                <button
                                    onClick={stopRecording}
                                    className="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 text-white px-8 py-4 rounded-full font-bold transition-all"
                                >
                                    <StopCircle className="w-6 h-6" />
                                    <span>Stop Recording</span>
                                </button>
                            )}

                            {videoUrl && !analyzing && (
                                <button
                                    onClick={handleRetake}
                                    className="flex items-center space-x-2 bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-full font-medium transition-colors"
                                >
                                    <RotateCcw className="w-5 h-5" />
                                    <span>Try Again</span>
                                </button>
                            )}
                        </div>

                        {analyzing && (
                            <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-6 text-center animate-pulse">
                                <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-3"></div>
                                <h3 className="text-lg font-semibold text-blue-400">Analyzing your response...</h3>
                                <p className="text-blue-200/70 text-sm">Our AI is evaluating your clarity, confidence, and content.</p>
                            </div>
                        )}
                    </div>

                    {/* Right Column: Feedback */}
                    <div className="space-y-6">
                        {feedback ? (
                            <div className="space-y-6 animate-fadeIn">
                                <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-8 border border-gray-700 shadow-xl">
                                    <div className="flex items-center justify-between mb-6">
                                        <h2 className="text-2xl font-bold text-white">AI Feedback</h2>
                                        <div className={`px-4 py-2 rounded-lg text-xl font-bold ${feedback.score >= 8 ? 'bg-green-500/20 text-green-400' :
                                                feedback.score >= 6 ? 'bg-yellow-500/20 text-yellow-400' :
                                                    'bg-red-500/20 text-red-400'
                                            }`}>
                                            Score: {feedback.score}/10
                                        </div>
                                    </div>

                                    <div className="space-y-6">
                                        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                                            <h3 className="flex items-center text-sm font-bold text-gray-400 uppercase tracking-wider mb-3">
                                                <Star className="w-4 h-4 mr-2 text-yellow-500" />
                                                Analysis
                                            </h3>
                                            <p className="text-gray-300 leading-relaxed">{feedback.feedback}</p>
                                        </div>

                                        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                                            <h3 className="flex items-center text-sm font-bold text-gray-400 uppercase tracking-wider mb-3">
                                                <MessageSquare className="w-4 h-4 mr-2 text-blue-500" />
                                                Tips for Improvement
                                            </h3>
                                            <p className="text-gray-300 leading-relaxed">{feedback.tips}</p>
                                        </div>

                                        {feedback.transcript && (
                                            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                                                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Transcript</h3>
                                                <p className="text-sm text-gray-500 italic">"{feedback.transcript}"</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-center p-8 border-2 border-dashed border-gray-800 rounded-xl text-gray-500">
                                <div className="bg-gray-800 p-4 rounded-full mb-4">
                                    <Video className="w-8 h-8 text-gray-600" />
                                </div>
                                <h3 className="text-lg font-medium text-gray-400 mb-2">Ready to Practice?</h3>
                                <p className="max-w-xs mx-auto">Record your answer to receive instant AI feedback on your performance.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
