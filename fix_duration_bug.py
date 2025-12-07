#!/usr/bin/env python3
"""Fix recording duration bug by adding recordingTimeRef"""

with open('frontend/app/conversation/[id]/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add recordingTimeRef after recordingIntervalRef
content = content.replace(
    "    const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);\n    const messagesEndRef",
    "    const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);\n    const recordingTimeRef = useRef(0);\n    const messagesEndRef"
)

# 2. Update onstop handler to use recordingTimeRef
content = content.replace(
    "            mediaRecorder.onstop = async () => {\n                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });\n                await sendAudioMessage(audioBlob, recordingTime);",
    "            mediaRecorder.onstop = async () => {\n                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });\n                await sendAudioMessage(audioBlob, recordingTimeRef.current);"
)

# 3. Initialize recordingTimeRef in startRecording
content = content.replace(
    "            mediaRecorder.start();\n            setIsRecording(true);\n            setRecordingTime(0);",
    "            mediaRecorder.start();\n            setIsRecording(true);\n            setRecordingTime(0);\n            recordingTimeRef.current = 0;"
)

# 4. Update recording interval to increment both state and ref
content = content.replace(
    "            recordingIntervalRef.current = setInterval(() => {\n                setRecordingTime(prev => prev + 1);\n            }, 1000);",
    "            recordingIntervalRef.current = setInterval(() => {\n                setRecordingTime(prev => prev + 1);\n                recordingTimeRef.current += 1;\n            }, 1000);"
)

with open('frontend/app/conversation/[id]/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed recording duration bug!")
print("Changes:")
print("  - Added recordingTimeRef")
print("  - Updated onstop handler to use recordingTimeRef.current")
print("  - Initialize recordingTimeRef in startRecording")
print("  - Update interval to increment both state and ref")
