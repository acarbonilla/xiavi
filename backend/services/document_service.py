"""
Document Processing Service for RAG Implementation
Handles PDF/TXT extraction, text chunking, and embedding generation
"""
import re
import io
from typing import List, Dict, Tuple
# import chardet
from PyPDF2 import PdfReader
import pdfplumber

import google.generativeai as genai
from django.conf import settings


class DocumentProcessor:
    """
    Process uploaded documents for RAG:
    - Extract text from PDF and TXT files
    - Split into semantic chunks with overlap
    - Generate embeddings using Gemini
    """
    
    # Chunking parameters
    CHUNK_SIZE = 800  # Target tokens per chunk (~600 words)
    CHUNK_OVERLAP = 100  # Overlap tokens to preserve context
    CHARS_PER_TOKEN = 4  # Approximate chars per token for estimation
    
    def __init__(self):
        """Initialize Gemini API for embeddings."""
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings")
        
        genai.configure(api_key=self.api_key)
        self.embedding_model = 'models/text-embedding-004'
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file using hybrid approach.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text as string
        
        Raises:
            Exception: If PDF extraction fails
        """
        text = ""
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            except Exception as inner_e:
                raise Exception(f"PDF extraction failed: {str(inner_e)}")
        
        if not text.strip():
            raise Exception("No text could be extracted from PDF")
        
        return text.strip()
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """
        Extract text from TXT file with encoding detection.
        
        Args:
            file_path: Path to TXT file
        
        Returns:
            Extracted text as string
        
        Raises:
            Exception: If text extraction fails
        """
        try:
            # Detect encoding
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                # Use charset_normalizer instead of chardet
                import charset_normalizer
                detected = charset_normalizer.from_bytes(raw_data).best()
                encoding = detected.encoding if detected else 'utf-8'
            
            # Read with detected encoding
            with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                text = file.read()
            
            if not text.strip():
                raise Exception("TXT file is empty")
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"TXT extraction failed: {str(e)}")
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extract text from document based on file type.
        
        Args:
            file_path: Path to document file
            file_type: 'pdf' or 'txt'
        
        Returns:
            Extracted text
        """
        if file_type == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type == 'txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks, preserving paragraph boundaries.
        
        Strategy:
        - Target chunk size: ~800 tokens (~3200 chars)
        - Overlap: ~100 tokens (~400 chars)
        - Preserve paragraph boundaries when possible
        - Split long paragraphs if needed
        
        Args:
            text: Full document text
        
        Returns:
            List of chunks with metadata:
            [
                {
                    'text': 'chunk text...',
                    'token_count': 750,
                    'chunk_index': 0
                },
                ...
            ]
        """
        # Clean up text - normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
        text = re.sub(r' +', ' ', text)  # Normalize spaces
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        target_chars = self.CHUNK_SIZE * self.CHARS_PER_TOKEN
        overlap_chars = self.CHUNK_OVERLAP * self.CHARS_PER_TOKEN
        
        for para in paragraphs:
            para_tokens = len(para) // self.CHARS_PER_TOKEN
            
            # If paragraph fits in current chunk, add it
            if current_tokens + para_tokens <= self.CHUNK_SIZE:
                current_chunk += para + "\n\n"
                current_tokens += para_tokens
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'token_count': current_tokens,
                        'chunk_index': chunk_index
                    })
                    chunk_index += 1
                    
                    # Start new chunk with overlap from end of previous chunk
                    overlap_text = current_chunk[-overlap_chars:] if len(current_chunk) > overlap_chars else ""
                    current_chunk = overlap_text
                    current_tokens = len(overlap_text) // self.CHARS_PER_TOKEN
                
                # If paragraph is too large, split it
                if para_tokens > self.CHUNK_SIZE:
                    # Split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sentence in sentences:
                        sentence_tokens = len(sentence) // self.CHARS_PER_TOKEN
                        
                        if current_tokens + sentence_tokens <= self.CHUNK_SIZE:
                            current_chunk += sentence + " "
                            current_tokens += sentence_tokens
                        else:
                            if current_chunk:
                                chunks.append({
                                    'text': current_chunk.strip(),
                                    'token_count': current_tokens,
                                    'chunk_index': chunk_index
                                })
                                chunk_index += 1
                            
                            current_chunk = sentence + " "
                            current_tokens = sentence_tokens
                else:
                    current_chunk += para + "\n\n"
                    current_tokens += para_tokens
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'token_count': current_tokens,
                'chunk_index': chunk_index
            })
        
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Gemini Embedding API.
        
        Args:
            text: Text to embed
        
        Returns:
            768-dimensional embedding vector
        
        Raises:
            Exception: If embedding generation fails
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document",
                title="Document chunk for RAG"
            )
            return result['embedding']
        
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query.
        
        Args:
            query: Search query text
        
        Returns:
            768-dimensional embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        
        except Exception as e:
            raise Exception(f"Query embedding generation failed: {str(e)}")
    
    def process_document(self, document_upload) -> Tuple[int, str]:
        """
        Full document processing pipeline:
        1. Extract text from file
        2. Chunk text intelligently
        3. Generate embeddings for each chunk
        4. Save chunks to database
        
        Args:
            document_upload: DocumentUpload model instance
        
        Returns:
            Tuple of (chunk_count, error_message)
            If successful: (chunk_count, '')
            If failed: (0, 'error message')
        """
        from apps.conversations.models import DocumentChunk
        
        try:
            # Extract text
            file_path = document_upload.file.path
            text = self.extract_text(file_path, document_upload.file_type)
            
            # Chunk text
            chunks = self.chunk_text(text)
            
            if not chunks:
                return (0, "No chunks generated from document")
            
            # Generate embeddings and save chunks
            for chunk_data in chunks:
                try:
                    embedding = self.generate_embedding(chunk_data['text'])
                    
                    DocumentChunk.objects.create(
                        document=document_upload,
                        chunk_index=chunk_data['chunk_index'],
                        text=chunk_data['text'],
                        embedding=embedding,
                        token_count=chunk_data['token_count']
                    )
                except Exception as e:
                    # Continue processing other chunks even if one fails
                    print(f"Warning: Failed to process chunk {chunk_data['chunk_index']}: {str(e)}")
                    continue
            
            # Update document processing status
            chunk_count = DocumentChunk.objects.filter(document=document_upload).count()
            document_upload.processed = True
            document_upload.chunk_count = chunk_count
            document_upload.save()
            
            return (chunk_count, '')
        
        except Exception as e:
            # Mark as processing failed
            error_msg = str(e)
            document_upload.processed = False
            document_upload.processing_error = error_msg
            document_upload.save()
            
            return (0, error_msg)
