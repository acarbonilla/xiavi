#!/usr/bin/env python3
"""
Script to apply simplified VAD changes to the conversation page.
This makes all the necessary edits in one go to avoid file corruption.
"""

import re

# Read the original file
with open('frontend/app/conversation/[id]/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add new state variables after line 20
content = content.replace(
    "    const [error, setError] = useState('');\n    const [useVAD, setUseVAD] = useState(true);",
    "    const [error, setError] = useState('');\n    const [silenceTimer, setSilenceTimer] = useState<number | null>(null);\n    const [useVAD, setUseVAD] = useState(true);"
)

content = content.replace(
    "    const [audioLevel, setAudioLevel] = useState(0); // Audio level for mic meter (0-100)\n\n    const mediaRecorderRef",
    "    const [audioLevel, setAudioLevel] = useState(0); // Audio level for mic meter (0-100)\n    const [sensitivity, setSensitivity] = useState(1.5); // Threshold multiplier (0.5-3.0)\n    const [isSpeaking, setIsSpeaking] = useState(false); // Track if user is speaking\n\n    const mediaRecorderRef"
)

# 2. Add new refs after line 33
content = content.replace(
    "    const vadCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);\n\n    useEffect",
    "    const vadCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);\n    const smoothedLevelRef = useRef(0);\n    const silenceStartTimeRef = useRef<number | null>(null);\n    const sensitivityRef = useRef(1.5);\n    const useVADRef = useRef(true);\n    const silenceDurationRef = useRef(4000);\n    const isSpeakingRef = useRef(false);\n\n    useEffect"
)

# 3. Add useEffect hooks after existing ones
content = content.replace(
    "    useEffect(() => {\n        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });\n    }, [messages]);\n\n    const fetchSession",
    "    useEffect(() => {\n        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });\n    }, [messages]);\n\n    // Keep refs in sync with state to avoid closure issues\n    useEffect(() => { sensitivityRef.current = sensitivity; }, [sensitivity]);\n    useEffect(() => { useVADRef.current = useVAD; }, [useVAD]);\n    useEffect(() => { silenceDurationRef.current = silenceDuration; }, [silenceDuration]);\n\n    const fetchSession"
)

# 4. Replace detectSilence function
old_detect_silence = """    const detectSilence = () => {
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
    };"""

new_detect_silence = """    const detectSilence = () => {
        if (!analyserRef.current) return;

        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyserRef.current.getByteFrequencyData(dataArray);

        // Calculate average volume
        const average = dataArray.reduce((a, b) => a + b) / bufferLength;
        const rawLevel = Math.min(100, (average / 128) * 100);

        // Apply smoothing to reduce jitter
        const SMOOTHING = 0.3;
        smoothedLevelRef.current = (SMOOTHING * rawLevel) + ((1 - SMOOTHING) * smoothedLevelRef.current);
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
                    console.log('✅ Auto-stopping due to silence');
                    stopRecording();
                    isSpeakingRef.current = false;
                    setIsSpeaking(false);
                }
            }
        }
    };"""

content = content.replace(old_detect_silence, new_detect_silence)

# 5. Update startRecording - add VAD initialization
content = content.replace(
    "            source.connect(analyserRef.current);\n\n            // Check audio level every 100ms",
    "            source.connect(analyserRef.current);\n\n            // Initialize VAD state\n            smoothedLevelRef.current = 0;\n            isSpeakingRef.current = false;\n            setIsSpeaking(false);\n            silenceStartTimeRef.current = null;\n            setSilenceTimer(null);\n\n            // Check audio level every 100ms"
)

# 6. Update stopRecording - add state reset
content = content.replace(
    "            setAudioLevel(0); // Reset audio level meter\n            if (recordingIntervalRef.current)",
    "            setAudioLevel(0);\n            setIsSpeaking(false);\n            isSpeakingRef.current = false;\n            if (recordingIntervalRef.current)"
)

# 7. Add sensitivity slider to settings panel
settings_addition = """
                                <p className="text-xs text-gray-600 mt-2">
                                    💡 Tip: ESL learners typically need 3-5 seconds between thoughts
                                </p>

                                {/* Sensitivity Slider */}
                                <div className="mb-4 pt-4 border-t border-gray-200">
                                    <div className="flex items-center justify-between mb-2">
                                        <label className="font-medium text-gray-900">Microphone Sensitivity</label>
                                        <span className="text-sm font-semibold text-primary-600">
                                            {sensitivity.toFixed(1)}x
                                        </span>
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
                                        💡 Lower = picks up quieter sounds (may trigger on noise)<br/>
                                        Higher = requires louder speech (better for noisy environments)
                                    </p>
                                </div>
                            </div>"""

content = content.replace(
    "                                <p className=\"text-xs text-gray-600 mt-2\">\n                                    💡 Tip: ESL learners typically need 3-5 seconds between thoughts\n                                </p>\n                            </div>",
    settings_addition
)

# Write the modified content
with open('frontend/app/conversation/[id]/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully applied all VAD changes!")
print("Changes made:")
print("  - Added state variables: silenceTimer, sensitivity, isSpeaking")
print("  - Added refs: smoothedLevelRef, silenceStartTimeRef, sensitivityRef, useVADRef, silenceDurationRef, isSpeakingRef")
print("  - Added useEffect hooks to sync refs with state")
print("  - Replaced detectSilence function with simplified VAD implementation")
print("  - Updated startRecording to initialize VAD state")
print("  - Updated stopRecording to reset VAD state")
print("  - Added sensitivity slider to settings panel")
