"""
RAG Diagnostic Script
Run this to check if your documents are properly processed and retrievable.
"""
from apps.conversations.models import ConversationSession, DocumentUpload, DocumentChunk
from services.gemini_service import GeminiService

def check_rag_system(session_id=None):
    """
    Check RAG system status for a specific session or all sessions.
    """
    print("=" * 60)
    print("RAG SYSTEM DIAGNOSTIC")
    print("=" * 60)
    
    if session_id:
        sessions = ConversationSession.objects.filter(id=session_id)
        print(f"\nChecking session ID: {session_id}")
    else:
        sessions = ConversationSession.objects.filter(documents__isnull=False).distinct()
        print(f"\nChecking all sessions with documents ({sessions.count()} found)")
    
    if not sessions.exists():
        print("❌ No sessions with documents found!")
        return
    
    for session in sessions:
        print(f"\n{'='*60}")
        print(f"Session ID: {session.id}")
        print(f"Topic: {session.topic.name if session.topic else 'None'}")
        print(f"Status: {session.status}")
        print(f"Documents: {session.documents.count()}")
        print("-" * 60)
        
        for doc in session.documents.all():
            status_icon = "✅" if doc.processed else "❌"
            print(f"\n{status_icon} Document: {doc.filename}")
            print(f"   - File size: {doc.file_size_kb} KB")
            print(f"   - Type: {doc.file_type}")
            print(f"   - Processed: {doc.processed}")
            print(f"   - Chunks: {doc.chunk_count}")
            
            if doc.processing_error:
                print(f"   - ⚠️  Error: {doc.processing_error}")
            
            # Check actual chunks in DB
            actual_chunks = DocumentChunk.objects.filter(document=doc)
            print(f"   - Actual chunks in DB: {actual_chunks.count()}")
            
            if actual_chunks.exists():
                first_chunk = actual_chunks.first()
                has_embedding = first_chunk.embedding is not None and len(first_chunk.embedding) > 0
                embed_icon = "✅" if has_embedding else "❌"
                print(f"   - {embed_icon} Embeddings: {len(first_chunk.embedding) if has_embedding else 0} dimensions")
                print(f"   - Sample text preview: {first_chunk.text[:100]}...")
        
        # Test retrieval if session has processed documents
        if session.documents.filter(processed=True).exists():
            print(f"\n{'─'*60}")
            print("Testing RAG Retrieval...")
            print("─" * 60)
            
            gemini = GeminiService()
            
            # Test with different queries
            test_queries = [
                "What is this document about?",
                "Can you summarize the main points?",
                "Tell me about the content"
            ]
            
            for query in test_queries:
                print(f"\n📝 Query: '{query}'")
                chunks = gemini.retrieve_relevant_chunks(session, query, top_k=3)
                
                if chunks:
                    print(f"   Retrieved {len(chunks)} chunks:")
                    for i, chunk in enumerate(chunks, 1):
                        similarity_icon = "🟢" if chunk['similarity'] > 0.35 else "🟡" if chunk['similarity'] > 0.25 else "🔴"
                        print(f"   {i}. {similarity_icon} {chunk['filename']}")
                        print(f"      Similarity: {chunk['similarity']:.3f}")
                        print(f"      Text: {chunk['text'][:80]}...")
                else:
                    print("   ❌ No chunks retrieved!")
    
    print(f"\n{'='*60}")
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - ✅ means working correctly")
    print("   - ❌ means there's an issue")
    print("   - Similarity > 0.30 is used in responses")
    print("   - 🟢 = High similarity (>0.35)")
    print("   - 🟡 = Medium similarity (0.25-0.35)")
    print("   - 🔴 = Low similarity (<0.25)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        session_id = int(sys.argv[1])
        check_rag_system(session_id)
    else:
        check_rag_system()
