'use client';

import { useState, useRef } from 'react';
import { Upload, File, X, CheckCircle, Loader } from 'lucide-react';
import { APIClient } from '@/lib/api';

interface Document {
    id: number;
    filename: string;
    file_size_kb: number;
    processed: boolean;
    chunk_count: number;
    uploaded_at: string;
}

interface DocumentUploadProps {
    sessionId: number;
    onUploadComplete?: () => void;
}

export default function DocumentUpload({ sessionId, onUploadComplete }: DocumentUploadProps) {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Load documents on mount
    const loadDocuments = async () => {
        try {
            const api = new APIClient();
            const docs = await api.getDocuments(sessionId);
            setDocuments(docs);
        } catch (err) {
            console.error('Failed to load documents:', err);
        }
    };

    // Initial load
    useState(() => {
        loadDocuments();
    });

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        // Validate file type
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (ext !== 'pdf' && ext !== 'txt') {
            setError('Only PDF and TXT files are supported');
            return;
        }

        // Validate file size (50MB)
        if (file.size > 50 * 1024 * 1024) {
            setError('File size must be less than 50MB');
            return;
        }

        // Check document limit
        if (documents.length >= 5) {
            setError('Maximum 5 documents per conversation');
            return;
        }

        setError(null);
        setUploading(true);

        try {
            const api = new APIClient();
            await api.uploadDocument(sessionId, file);
            await loadDocuments();
            if (onUploadComplete) onUploadComplete();

            // Reset input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        } catch (err: any) {
            setError(err.response?.data?.error || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (docId: number) => {
        try {
            const api = new APIClient();
            await api.deleteDocument(docId);
            await loadDocuments();
        } catch (err) {
            console.error('Delete failed:', err);
        }
    };

    return (
        <div className="space-y-4">
            {/* Upload Button */}
            <div>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.txt"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="document-upload"
                />
                <label
                    htmlFor="document-upload"
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 border-dashed 
                        ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:bg-gray-50'}
                        ${documents.length >= 5 ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                >
                    {uploading ? (
                        <>
                            <Loader className="w-5 h-5 animate-spin" />
                            <span>Uploading & Processing...</span>
                        </>
                    ) : (
                        <>
                            <Upload className="w-5 h-5" />
                            <span>Upload PDF or TXT ({documents.length}/5)</span>
                        </>
                    )}
                </label>
            </div>

            {/* Error Message */}
            {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                    {error}
                </div>
            )}

            {/* Document List */}
            {documents.length > 0 && (
                <div className="space-y-2">
                    <h4 className="text-sm font-semibold text-gray-700">Uploaded Documents</h4>
                    {documents.map((doc) => (
                        <div
                            key={doc.id}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                        >
                            <div className="flex items-center gap-3 flex-1">
                                <File className="w-4 h-4 text-blue-500" />
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium truncate">{doc.filename}</p>
                                    <p className="text-xs text-gray-500">
                                        {doc.file_size_kb} KB • {doc.chunk_count} chunks
                                    </p>
                                </div>
                                {doc.processed ? (
                                    <CheckCircle className="w-4 h-4 text-green-500" />
                                ) : (
                                    <Loader className="w-4 h-4 animate-spin text-blue-500" />
                                )}
                            </div>
                            <button
                                onClick={() => handleDelete(doc.id)}
                                className="p-1 hover:bg-gray-200 rounded"
                            >
                                <X className="w-4 h-4 text-gray-500" />
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
