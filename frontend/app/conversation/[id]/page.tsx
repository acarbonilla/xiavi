'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ConversationSession, ConversationMessage } from '@/types';
import { Mic, MicOff, Send, X, Loader2, MessageCircle, ArrowLeft, Settings } from 'lucide-react';
import Link from 'next/link';

export default function ConversationPage() {
    const params = useParams();
    const router = useRouter();
    const sessionId = parseInt(params.id as string);

    const [session, setSession] = useState<ConversationSession | null>(null);
    const [messages, setMessages] = useState<ConversationMessage[]>([]);
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [error, setError] = useState('');
    const [useVAD, setUseVAD] = useState(true); // Voice Activity Detection enabled by default
    const [silenceDuration, setSilenceDuration] = useState(4000); // 4 seconds for ESL learners
    const [showSettings, setShowSettings] = useState(false);
    const [audioLevel, setAudioLevel] = useState(0); // Audio level for mic meter (0-100)

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const vadCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        fetchSession();
        fetchMessages();
    }, [sessionId]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const fetchSession = async () => {
        try {
            const data = await api.getConversation(sessionId);
            setSession(data);
        } catch (error) {
            console.error('Error fetching session:', error);
            setError('Failed to load conversation');
        }
    };

    const fetchMessages = async () => {
        try {
            const data = await api.getConversationMessages(sessionId);
            setMessages(data);
        } catch (error) {
            console.error('Error fetching messages:', error);
        }
    };

    const detectSilence = () => {
        if (!analyserRef.current) return;

        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyserRef.current.getByteFrequencyData(dataArray);

        // Calculate average volume
        const average = dataArray.reduce((a, b) => a + b) / bufferLength;
        const threshold = 10; // Silence threshold (adjust if needed)

        // Update audio level for visual meter (normalize to 0-100)
        const normalizedLevel = Math.min(100, (average / 128) * 100);
        setAudioLevel(normalizedLevel);

        if (average < threshold) {
            // Silence detected - start countdown if not already started
            if (!silenceTimeoutRef.current && useVAD) {
                silenceTimeoutRef.current = setTimeout(() => {
                    console.log('Auto-stopping due to silence');
                    stopRecording();
                }, silenceDuration);
            }
        } else {
            // Sound detected - reset silence timer
            if (silenceTimeoutRef.current) {
                clearTimeout(silenceTimeoutRef.current);
                silenceTimeoutRef.current = null;
            }
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            // Set up audio analysis for mic meter and VAD
            audioContextRef.current = new AudioContext();
            const source = audioContextRef.current.createMediaStreamSource(stream);
            analyserRef.current = audioContextRef.current.createAnalyser();
            analyserRef.current.fftSize = 2048;
            source.connect(analyserRef.current);

            // Check audio level every 100ms (for VAD and visual meter)
            vadCheckIntervalRef.current = setInterval(detectSilence, 100);

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                await sendAudioMessage(audioBlob, recordingTime);
                stream.getTracks().forEach(track => track.stop());

                // Clean up VAD
                if (vadCheckIntervalRef.current) {
                    clearInterval(vadCheckIntervalRef.current);
                }
                if (silenceTimeoutRef.current) {
                    clearTimeout(silenceTimeoutRef.current);
                    silenceTimeoutRef.current = null;
                }
                if (audioContextRef.current) {
                    audioContextRef.current.close();
                }
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingTime(0);

            recordingIntervalRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);
        } catch (error) {
            console.error('Error starting recording:', error);
            setError('Failed to access microphone');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            setAudioLevel(0); // Reset audio level meter
            if (recordingIntervalRef.current) {
                clearInterval(recordingIntervalRef.current);
            }
        }
    };

    const sendAudioMessage = async (audioBlob: Blob, duration: number) => {
        setIsProcessing(true);
        setError(''); // Clear any previous errors
        
        try {
            // Check if blob is empty
            if (audioBlob.size === 0) {
                throw new Error('Audio recording is empty. Please ensure your microphone is working.');
            }
            
            console.log(`Sending audio message: ${audioBlob.size} bytes, ${duration}s duration`);
            const response = await api.sendAudioMessage(sessionId, audioBlob, duration);

            // Add user message
            const userMessage: ConversationMessage = {
                id: response.user_message.id,
                session: sessionId,
                role: 'user',
                text: response.user_message.text,
                duration: duration,
                timestamp: response.user_message.timestamp,
            };

            // Add AI message
            const aiMessage: ConversationMessage = {
                id: response.ai_message.id,
                session: sessionId,
                role: 'ai',
                text: response.ai_message.text,
                duration: 0,
                timestamp: response.ai_message.timestamp,
            };

            setMessages(prev => [...prev, userMessage, aiMessage]);

            // Play AI audio response
            if (response.ai_audio) {
                playAudioFromHex(response.ai_audio);
            }
        } catch (error: any) {
            console.error('Error sending audio:', error);
            
            // Extract error message from response
            let errorMessage = 'Failed to send message';
            
            if (error.response?.data?.error) {
                errorMessage = error.response.data.error;
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            setError(errorMessage);
        } finally {
            setIsProcessing(false);
            setRecordingTime(0);
        }
    };

    const playAudioFromHex = (hexString: string) => {
        try {
            const bytes = new Uint8Array(hexString.match(/.{1,2}/g)!.map(byte => parseInt(byte, 16)));
            const audioBlob = new Blob([bytes], { type: 'audio/mp3' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            audio.play();
        } catch (error) {
            console.error('Error playing audio:', error);
        }
    };

    const endConversation = async () => {
        try {
            await api.endConversation(sessionId);
            router.push(`/conversation/${sessionId}/feedback`);
        } catch (error) {
            console.error('Error ending conversation:', error);
            setError('Failed to end conversation');
        }
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    if (!session) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-4 py-4">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">{session.topic_name}</h1>
                            <p className="text-sm text-gray-600">
                                {messages.filter(m => m.role === 'user').length} messages
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={() => setShowSettings(!showSettings)}
                            className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
                        >
                            <Settings className="w-5 h-5" />
                        </button>
                        <button
                            onClick={endConversation}
                            className="btn-outline py-2 px-4 text-sm"
                        >
                            End & Get Feedback
                        </button>
                    </div>
                </div>

                {/* Settings Panel */}
                {showSettings && (
                    <div className="max-w-4xl mx-auto mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                        <h3 className="font-semibold text-gray-900 mb-3">Recording Settings</h3>

                        {/* VAD Toggle */}
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <p className="font-medium text-gray-900">Auto-Stop Recording</p>
                                <p className="text-sm text-gray-600">Automatically stop when you pause speaking</p>
                            </div>
                            <button
                                onClick={() => setUseVAD(!useVAD)}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${useVAD ? 'bg-primary-600' : 'bg-gray-300'
                                    }`}
                            >
                                <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${useVAD ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                />
                            </button>
                        </div>

                        {/* Silence Duration Slider */}
                        {useVAD && (
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="font-medium text-gray-900">Pause Duration</label>
                                    <span className="text-sm font-semibold text-primary-600">
                                        {(silenceDuration / 1000).toFixed(1)}s
                                    </span>
                                </div>
                                <input
                                    type="range"
                                    min="1000"
                                    max="8000"
                                    step="500"
                                    value={silenceDuration}
                                    onChange={(e) => setSilenceDuration(parseInt(e.target.value))}
                                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                                />
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <span>1s (Quick)</span>
                                    <span>4s (ESL Friendly)</span>
                                    <span>8s (Thoughtful)</span>
                                </div>
                                <p className="text-xs text-gray-600 mt-2">
                                    💡 Tip: ESL learners typically need 3-5 seconds between thoughts
                                </p>
                            </div>
                        )}
                    </div>
                )}
            </header>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-6">
                <div className="max-w-4xl mx-auto space-y-4">
                    {messages.length === 0 && (
                        <div className="text-center py-12">
                            <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                            <p className="text-gray-500">
                                {useVAD
                                    ? 'Start speaking! Recording will auto-stop after you pause.'
                                    : 'Press the mic to start, press stop when done speaking.'}
                            </p>
                        </div>
                    )}

                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[70%] rounded-2xl px-4 py-3 ${message.role === 'user'
                                    ? 'bg-primary-600 text-white'
                                    : 'bg-white border border-gray-200 text-gray-900'
                                    }`}
                            >
                                <p className="text-sm">{message.text}</p>
                                {message.duration > 0 && (
                                    <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-primary-100' : 'text-gray-500'}`}>
                                        {formatTime(message.duration)}
                                    </p>
                                )}
                            </div>
                        </div>
                    ))}

                    {isProcessing && (
                        <div className="flex justify-start">
                            <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                                <div className="flex items-center space-x-2">
                                    <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                                    <p className="text-sm text-gray-600">AI is thinking...</p>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="px-4 py-2 bg-red-50 border-t border-red-200">
                    <div className="max-w-4xl mx-auto">
                        <p className="text-sm text-red-800">{error}</p>
                    </div>
                </div>
            )}

            {/* Recording Controls */}
            <div className="bg-white border-t border-gray-200 px-4 py-6">
                <div className="max-w-4xl mx-auto">
                    <div className="flex items-center justify-center space-x-4">
                        {!isRecording && !isProcessing && (
                            <button
                                onClick={startRecording}
                                className="w-16 h-16 bg-primary-600 hover:bg-primary-700 rounded-full flex items-center justify-center transition-all transform hover:scale-110 shadow-lg"
                            >
                                <Mic className="w-8 h-8 text-white" />
                            </button>
                        )}

                        {isRecording && (
                            <>
                                <div className="flex items-center space-x-4">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                                        <span className="text-lg font-mono font-semibold text-gray-900">
                                            {formatTime(recordingTime)}
                                        </span>
                                    </div>
                                    {!useVAD && (
                                        <button
                                            onClick={stopRecording}
                                            className="w-16 h-16 bg-red-600 hover:bg-red-700 rounded-full flex items-center justify-center transition-all shadow-lg"
                                        >
                                            <MicOff className="w-8 h-8 text-white" />
                                        </button>
                                    )}
                                </div>
                            </>
                        )}

                        {isProcessing && (
                            <div className="flex items-center space-x-2">
                                <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
                                <span className="text-gray-600">Processing...</span>
                            </div>
                        )}
                    </div>

                    {/* Microphone Level Meter */}
                    {isRecording && (
                        <div className="mt-6 mb-2">
                            <div className="flex items-center justify-center space-x-3">
                                <Mic className="w-5 h-5 text-gray-500" />
                                <div className="flex-1 max-w-md">
                                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                        <div
                                            className="h-full transition-all duration-100 ease-out rounded-full"
                                            style={{
                                                width: `${audioLevel}%`,
                                                background: audioLevel > 60
                                                    ? 'linear-gradient(to right, #22c55e, #ef4444)'
                                                    : audioLevel > 30
                                                        ? 'linear-gradient(to right, #22c55e, #eab308)'
                                                        : '#22c55e'
                                            }}
                                        />
                                    </div>
                                </div>
                                <span className="text-xs font-mono text-gray-500 w-10 text-right">
                                    {Math.round(audioLevel)}%
                                </span>
                            </div>
                        </div>
                    )}

                    <p className="text-center text-sm text-gray-500 mt-4">
                        {isRecording
                            ? useVAD
                                ? `Recording... Will auto-stop after ${silenceDuration / 1000}s of silence`
                                : 'Tap to stop recording'
                            : useVAD
                                ? 'Tap to start speaking (auto-stop enabled)'
                                : 'Tap to start speaking'}
                    </p>
                </div>
            </div>
        </div>
    );
}
