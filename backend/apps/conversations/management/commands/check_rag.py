"""
Management command to diagnose RAG system
"""
from django.core.management.base import BaseCommand
from apps.conversations.models import ConversationSession, DocumentUpload, DocumentChunk
from services.gemini_service import GeminiService


class Command(BaseCommand):
    help = 'Check RAG system status and test document retrieval'

    def add_arguments(self, parser):
        parser.add_argument(
            '--session',
            type=int,
            help='Specific session ID to check',
        )

    def handle(self, *args, **options):
        session_id = options.get('session')
        
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("RAG SYSTEM DIAGNOSTIC"))
        self.stdout.write("=" * 60)
        
        if session_id:
            sessions = ConversationSession.objects.filter(id=session_id)
            self.stdout.write(f"\nChecking session ID: {session_id}")
        else:
            sessions = ConversationSession.objects.filter(documents__isnull=False).distinct()
            self.stdout.write(f"\nChecking all sessions with documents ({sessions.count()} found)")
        
        if not sessions.exists():
            self.stdout.write(self.style.ERROR("No sessions with documents found!"))
            return
        
        for session in sessions:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Session ID: {session.id}")
            self.stdout.write(f"Topic: {session.topic.name if session.topic else 'None'}")
            self.stdout.write(f"Status: {session.status}")
            self.stdout.write(f"Documents: {session.documents.count()}")
            self.stdout.write("-" * 60)
            
            for doc in session.documents.all():
                status_icon = "✅" if doc.processed else "❌"
                self.stdout.write(f"\n{status_icon} Document: {doc.filename}")
                self.stdout.write(f"   - File size: {doc.file_size / 1024:.2f} KB")
                self.stdout.write(f"   - Type: {doc.file_type}")
                self.stdout.write(f"   - Processed: {doc.processed}")
                self.stdout.write(f"   - Chunks: {doc.chunk_count}")
                
                if doc.processing_error:
                    self.stdout.write(self.style.ERROR(f"   - Error: {doc.processing_error}"))
                
                # Check actual chunks in DB
                actual_chunks = DocumentChunk.objects.filter(document=doc)
                self.stdout.write(f"   - Actual chunks in DB: {actual_chunks.count()}")
                
                if actual_chunks.exists():
                    first_chunk = actual_chunks.first()
                    has_embedding = first_chunk.embedding is not None and len(first_chunk.embedding) > 0
                    embed_icon = "✅" if has_embedding else "❌"
                    embed_dims = len(first_chunk.embedding) if has_embedding else 0
                    self.stdout.write(f"   - {embed_icon} Embeddings: {embed_dims} dimensions")
                    preview = first_chunk.text[:80].replace('\n', ' ')
                    self.stdout.write(f"   - Sample: {preview}...")
            
            # Test retrieval if session has processed documents
            if session.documents.filter(processed=True).exists():
                self.stdout.write(f"\n{'─'*60}")
                self.stdout.write("Testing RAG Retrieval...")
                self.stdout.write("─" * 60)
                
                gemini = GeminiService()
                
                # Test with different queries
                test_queries = [
                    "What is this document about?",
                    "Can you summarize the main points?",
                ]
                
                for query in test_queries:
                    self.stdout.write(f"\nQuery: '{query}'")
                    chunks = gemini.retrieve_relevant_chunks(session, query, top_k=3)
                    
                    if chunks:
                        self.stdout.write(self.style.SUCCESS(f"   Retrieved {len(chunks)} chunks:"))
                        for i, chunk in enumerate(chunks, 1):
                            similarity_icon = "🟢" if chunk['similarity'] > 0.35 else "🟡" if chunk['similarity'] > 0.25 else "🔴"
                            self.stdout.write(f"   {i}. {similarity_icon} {chunk['filename']}")
                            self.stdout.write(f"      Similarity: {chunk['similarity']:.3f}")
                            text_preview = chunk['text'][:60].replace('\n', ' ')
                            self.stdout.write(f"      Text: {text_preview}...")
                    else:
                        self.stdout.write(self.style.ERROR("   No chunks retrieved!"))
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS("DIAGNOSTIC COMPLETE"))
        self.stdout.write("=" * 60)
        self.stdout.write("\nTips:")
        self.stdout.write("   - Similarity > 0.30 is used in responses")
        self.stdout.write("   - 🟢 = High similarity (>0.35)")
        self.stdout.write("   - 🟡 = Medium similarity (0.25-0.35)")
        self.stdout.write("   - 🔴 = Low similarity (<0.25)")
