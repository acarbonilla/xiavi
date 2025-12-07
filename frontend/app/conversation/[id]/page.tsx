"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { ConversationSession, ConversationMessage } from "@/types";
import { Mic, MicOff, Send, X, Loader2, MessageCircle, ArrowLeft, Settings, FileText } from "lucide-react";
import Link from "next/link";
import DocumentUpload from "@/components/DocumentUpload";

export default function ConversationPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = parseInt(params.id as string);

  const [session, setSession] = useState<ConversationSession | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState("");
  const [silenceTimer, setSilenceTimer] = useState<number | null>(null);
  const [useVAD, setUseVAD] = useState(true); // Voice Activity Detection enabled by default
  const [silenceDuration, setSilenceDuration] = useState(4000); // 4 seconds for ESL learners
  const [showSettings, setShowSettings] = useState(false);
  const [showDocuments, setShowDocuments] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0); // Audio level for mic meter (0-100)
  const [sensitivity, setSensitivity] = useState(1.5); // Threshold multiplier (0.5-3.0)
  const [isSpeaking, setIsSpeaking] = useState(false); // Track if user is speaking

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const recordingTimeRef = useRef(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const vadCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const smoothedLevelRef = useRef(0);
  const silenceStartTimeRef = useRef<number | null>(null);
  const sensitivityRef = useRef(1.5);
  const useVADRef = useRef(true);
  const silenceDurationRef = useRef(4000);
  const isSpeakingRef = useRef(false);

  useEffect(() => {
    fetchSession();
    fetchMessages();
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Keep refs in sync with state to avoid closure issues
  useEffect(() => {
    sensitivityRef.current = sensitivity;
  }, [sensitivity]);
  useEffect(() => {
    useVADRef.current = useVAD;
  }, [useVAD]);
  useEffect(() => {
    silenceDurationRef.current = silenceDuration;
  }, [silenceDuration]);

  const fetchSession = async () => {
    try {
      const data = await api.getConversation(sessionId);
      setSession(data);
    } catch (error) {
      console.error("Error fetching session:", error);
      setError("Failed to load conversation");
    }
  };

  const fetchMessages = async () => {
    try {
      const data = await api.getConversationMessages(sessionId);
      setMessages(data);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  };

  const detectSilence = () => {
    if (!analyserRef.current) return;

    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserRef.current.getByteFrequencyData(dataArray);

    // Calculate average volume
    const average = dataArray.reduce((a, b) => a + b) / bufferLength;
    const rawLevel = Math.min(100, (average / 128) * 100);

    // Apply smoothing to reduce jitter
    const SMOOTHING = 0.3;
    smoothedLevelRef.current = SMOOTHING * rawLevel + (1 - SMOOTHING) * smoothedLevelRef.current;
    const smoothedLevel = smoothedLevelRef.current;

    // Update visual meter
    setAudioLevel(smoothedLevel);

    // Calculate threshold based on sensitivity
    // sensitivity 0.5 = 7.5% threshold (very sensitive)
    // sensitivity 1.5 = 22.5% threshold (balanced)
    // sensitivity 3.0 = 45% threshold (less sensitive)
    const BASE_THRESHOLD = 15;
    const speechThreshold = BASE_THRESHOLD * sensitivityRef.current;
    const silenceThreshold = speechThreshold * 0.7; // Lower threshold for silence

    // Track speaking state
    if (smoothedLevel > speechThreshold) {
      // Speech detected
      isSpeakingRef.current = true;
      setIsSpeaking(true);

      // Reset silence timer
      if (silenceStartTimeRef.current) {
        silenceStartTimeRef.current = null;
        setSilenceTimer(null);
      }
    } else if (smoothedLevel < silenceThreshold && isSpeakingRef.current) {
      // Silence after speech - start countdown
      if (useVADRef.current) {
        if (!silenceStartTimeRef.current) {
          silenceStartTimeRef.current = Date.now();
        }

        const elapsed = Date.now() - silenceStartTimeRef.current;
        const remaining = Math.max(0, silenceDurationRef.current - elapsed);
        setSilenceTimer(remaining);

        if (remaining === 0) {
          console.log("✅ Auto-stopping due to silence");
          stopRecording();
          isSpeakingRef.current = false;
          setIsSpeaking(false);
        }
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

      // Initialize VAD state
      smoothedLevelRef.current = 0;
      isSpeakingRef.current = false;
      setIsSpeaking(false);
      silenceStartTimeRef.current = null;
      setSilenceTimer(null);

      // Check audio level every 100ms (for VAD and visual meter)
      vadCheckIntervalRef.current = setInterval(detectSilence, 100);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        await sendAudioMessage(audioBlob, recordingTimeRef.current);
        stream.getTracks().forEach((track) => track.stop());

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
      recordingTimeRef.current = 0;

      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
        recordingTimeRef.current += 1;
      }, 1000);
    } catch (error) {
      console.error("Error starting recording:", error);
      setError("Failed to access microphone");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setAudioLevel(0);
      setIsSpeaking(false);
      isSpeakingRef.current = false;
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    }
  };

  const sendAudioMessage = async (audioBlob: Blob, duration: number) => {
    setIsProcessing(true);
    setError(""); // Clear any previous errors

    try {
      // Check if blob is empty
      if (audioBlob.size === 0) {
        throw new Error("Audio recording is empty. Please ensure your microphone is working.");
      }

      console.log(`Sending audio message: ${audioBlob.size} bytes, ${duration}s duration`);
      const response = await api.sendAudioMessage(sessionId, audioBlob, duration);

      // Add user message
      const userMessage: ConversationMessage = {
        id: response.user_message.id,
        session: sessionId,
        role: "user",
        text: response.user_message.text,
        duration: duration,
        timestamp: response.user_message.timestamp,
      };

      // Add AI message
      const aiMessage: ConversationMessage = {
        id: response.ai_message.id,
        session: sessionId,
        role: "ai",
        text: response.ai_message.text,
        duration: 0,
        timestamp: response.ai_message.timestamp,
      };

      setMessages((prev) => [...prev, userMessage, aiMessage]);

      // Play AI audio response
      if (response.ai_audio) {
        playAudioFromHex(response.ai_audio);
      }
    } catch (error: any) {
      console.error("Error sending audio:", error);

      // Extract error message from response
      let errorMessage = "Failed to send message";

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
      const bytes = new Uint8Array(hexString.match(/.{1,2}/g)!.map((byte) => parseInt(byte, 16)));
      const audioBlob = new Blob([bytes], { type: "audio/mp3" });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error("Error playing audio:", error);
    }
  };

  const endConversation = async () => {
    try {
      await api.endConversation(sessionId);
      router.push("/dashboard");
    } catch (error) {
      console.error("Error ending conversation:", error);
      setError("Failed to end conversation");
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50/30 via-white to-white flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-20 h-20 mx-auto mb-6">
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-primary-500 to-purple-500 opacity-75 animate-ping"></div>
            <div
              className="relative w-20 h-20 rounded-full bg-gradient-to-r from-primary-600 to-purple-600 animate-spin"
              style={{ borderTopColor: "transparent", borderWidth: "4px" }}
            ></div>
          </div>
          <p className="text-gray-600 font-medium">Loading conversation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50/30 via-white to-white flex flex-col">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 px-4 py-4 shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-6 h-6" />
            </Link>
            <div>
              <h1 className="text-xl font-bold text-gray-900">{session.topic_name}</h1>
              <p className="text-sm text-gray-600">{messages.filter((m) => m.role === "user").length} messages</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                setShowDocuments(!showDocuments);
                setShowSettings(false);
              }}
              className={`p-2 rounded-lg hover:bg-gray-100 ${
                showDocuments ? "text-primary-600 bg-primary-50" : "text-gray-600"
              }`}
              title="Documents"
            >
              <FileText className="w-5 h-5" />
            </button>
            <button
              onClick={() => {
                setShowSettings(!showSettings);
                setShowDocuments(false);
              }}
              className={`p-2 rounded-lg hover:bg-gray-100 ${
                showSettings ? "text-primary-600 bg-primary-50" : "text-gray-600"
              }`}
            >
              <Settings className="w-5 h-5" />
            </button>
            <button onClick={endConversation} className="btn-outline py-2 px-4 text-sm">
              End Conversation
            </button>
          </div>
        </div>

        {/* Documents Panel */}
        {showDocuments && (
          <div className="max-w-4xl mx-auto mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Conversation Documents</h3>
              <button onClick={() => setShowDocuments(false)} className="text-gray-500 hover:text-gray-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <DocumentUpload sessionId={sessionId} />
          </div>
        )}

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
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  useVAD ? "bg-primary-600" : "bg-gray-300"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    useVAD ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>

            {/* Silence Duration Slider */}
            {useVAD && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="font-medium text-gray-900">Pause Duration</label>
                  <span className="text-sm font-semibold text-primary-600">{(silenceDuration / 1000).toFixed(1)}s</span>
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

                {/* Sensitivity Slider */}
                <div className="mb-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <label className="font-medium text-gray-900">Microphone Sensitivity</label>
                    <span className="text-sm font-semibold text-primary-600">{sensitivity.toFixed(1)}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="3.0"
                    step="0.1"
                    value={sensitivity}
                    onChange={(e) => setSensitivity(parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0.5x (Very Sensitive)</span>
                    <span>1.5x (Balanced)</span>
                    <span>3.0x (Less Sensitive)</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-2">
                    💡 Lower = picks up quieter sounds (may trigger on noise)
                    <br />
                    Higher = requires louder speech (better for noisy environments)
                  </p>
                </div>
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
                  ? "Start speaking! Recording will auto-stop after you pause."
                  : "Press the mic to start, press stop when done speaking."}
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} ${
                message.role === "user" ? "animate-slide-in-right" : "animate-slide-in-left"
              }`}
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div
                className={`max-w-[70%] rounded-2xl px-4 py-3 shadow-md hover:shadow-lg transition-all duration-300 ${
                  message.role === "user"
                    ? "bg-gradient-to-br from-primary-600 to-primary-700 text-white"
                    : "bg-white border border-gray-200 text-gray-900"
                }`}
              >
                <p className="text-sm leading-relaxed">{message.text}</p>
                {message.duration > 0 && (
                  <div className="mt-2">
                    {message.audio_file && (
                      <audio
                        controls
                        src={message.audio_file}
                        className="w-full h-8 mb-1"
                        style={{ maxWidth: "240px" }}
                      />
                    )}
                    <p className={`text-xs ${message.role === "user" ? "text-primary-100" : "text-gray-500"}`}>
                      {formatTime(message.duration)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isProcessing && (
            <div className="flex justify-start animate-slide-in-left">
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-4 shadow-md">
                <div className="flex items-center space-x-3">
                  {/* Animated thinking dots */}
                  <div className="flex items-center space-x-1">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                  <p className="text-sm text-gray-600 font-medium">AI is thinking...</p>
                </div>
                {/* Audio wave visualization */}
                <div className="audio-wave mt-2">
                  <div className="audio-wave-bar" style={{ height: "12px" }}></div>
                  <div className="audio-wave-bar" style={{ height: "20px" }}></div>
                  <div className="audio-wave-bar" style={{ height: "16px" }}></div>
                  <div className="audio-wave-bar" style={{ height: "24px" }}></div>
                  <div className="audio-wave-bar" style={{ height: "14px" }}></div>
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
                className="w-20 h-20 bg-gradient-to-br from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 rounded-full flex items-center justify-center transition-all transform hover:scale-110 shadow-xl hover:shadow-2xl animate-pulse-ring"
              >
                <Mic className="w-9 h-9 text-white drop-shadow-md" />
              </button>
            )}

            {isRecording && (
              <>
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-3 bg-white/90 backdrop-blur-sm px-6 py-3 rounded-full shadow-md">
                    <div className="relative flex items-center">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                      <div className="absolute w-3 h-3 bg-red-500 rounded-full animate-ping"></div>
                    </div>
                    <span className="text-xl font-mono font-bold text-gray-900">{formatTime(recordingTime)}</span>
                  </div>
                  {!useVAD && (
                    <button
                      onClick={stopRecording}
                      className="w-16 h-16 bg-gradient-to-br from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 rounded-full flex items-center justify-center transition-all shadow-xl hover:scale-110 animate-glow"
                    >
                      <MicOff className="w-8 h-8 text-white drop-shadow-md" />
                    </button>
                  )}
                </div>
              </>
            )}

            {isProcessing && (
              <div className="flex flex-col items-center space-y-3 animate-slide-up">
                <div className="relative">
                  <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-600"></div>
                  <div className="absolute inset-0 animate-ping rounded-full border-4 border-primary-400 opacity-20"></div>
                </div>
                <span className="text-gray-700 font-medium">Processing your message...</span>
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
                        background:
                          audioLevel > 60
                            ? "linear-gradient(to right, #22c55e, #ef4444)"
                            : audioLevel > 30
                            ? "linear-gradient(to right, #22c55e, #eab308)"
                            : "#22c55e",
                      }}
                    />
                  </div>
                </div>
                <span className="text-xs font-mono text-gray-500 w-10 text-right">{Math.round(audioLevel)}%</span>
              </div>
            </div>
          )}

          <p className="text-center text-sm text-gray-500 mt-4">
            {isRecording
              ? useVAD
                ? `Recording... Will auto-stop after ${silenceDuration / 1000}s of silence`
                : "Tap to stop recording"
              : useVAD
              ? "Tap to start speaking (auto-stop enabled)"
              : "Tap to start speaking"}
          </p>
        </div>
      </div>
    </div>
  );
}
