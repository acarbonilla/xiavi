'use client';

interface AudioPlayerProps {
    audioUrl: string;
    className?: string;
}

export default function AudioPlayer({ audioUrl, className = '' }: AudioPlayerProps) {
    return (
        <div className={`bg-gray-50 rounded-lg p-4 ${className}`}>
            <audio controls className="w-full">
                <source src={audioUrl} type="audio/webm" />
                <source src={audioUrl} type="audio/mp3" />
                Your browser does not support the audio element.
            </audio>
        </div>
    );
}
