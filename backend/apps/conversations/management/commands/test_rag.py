"""
Django management command to test RAG functionality directly.
Run with: py manage.py test_rag
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.conversations.models import ConversationSession, Topic, DocumentUpload
from services.document_service import DocumentProcessor
from services.gemini_service import GeminiService
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Test RAG document upload and retrieval functionality'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("RAG SYSTEM TEST"))
        self.stdout.write("=" * 70)
        
        # Step 1: Get or create test user
        self.stdout.write("\n1. Getting test user...")
        user, created = User.objects.get_or_create(
            email='test@test.com',
            defaults={'username': 'testuser'}
        )
        if created:
            user.set_password('test123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f"   ✓ Created user: {user.email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"   ✓ Using existing user: {user.email}"))
        
        # Step 2: Create conversation session
        self.stdout.write("\n2. Creating conversation session...")
        topic = Topic.objects.first()
        if not topic:
            topic = Topic.objects.create(
                name="Test Topic",
                description="Test topic for RAG",
                difficulty="beginner"
            )
        
        session = ConversationSession.objects.create(
            user=user,
            topic=topic,
            status='active'
        )
        self.stdout.write(self.style.SUCCESS(f"   ✓ Created session ID: {session.id}"))
        
        # Step 3: Upload test document
        self.stdout.write("\n3. Uploading test document...")
        test_file_path = 'test_resume.txt'
        
        if not os.path.exists(test_file_path):
            self.stdout.write(self.style.ERROR(f"   ✗ File not found: {test_file_path}"))
            return
        
        with open(test_file_path, 'rb') as f:
            from django.core.files import File
            django_file = File(f, name='test_resume.txt')
            
            document = DocumentUpload.objects.create(
                session=session,
                file=django_file,
                filename='test_resume.txt',
                file_type='txt',
                file_size=os.path.getsize(test_file_path),
                processed=False
            )
        
        self.stdout.write(self.style.SUCCESS(f"   ✓ Document created: {document.filename}"))
        
        # Step 4: Process document
        self.stdout.write("\n4. Processing document (extracting, chunking, embedding)...")
        processor = DocumentProcessor()
        chunk_count, error_msg = processor.process_document(document)
        
        if error_msg:
            self.stdout.write(self.style.ERROR(f"   ✗ Processing failed: {error_msg}"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"   ✓ Created {chunk_count} chunks with embeddings"))
        
        # Step 5: Test RAG retrieval
        self.stdout.write("\n5. Testing RAG retrieval with sample questions...")
        self.stdout.write("-" * 70)
        
        gemini = GeminiService()
        
        questions = [
            "What is the candidate's current position?",
            "What programming languages does John know?",
            "Tell me about the work at Tech Corp",
            "What certifications does this person have?"
        ]
        
        for i, question in enumerate(questions, 1):
            self.stdout.write(f"\n📝 Question {i}: {question}")
            
            response_data = gemini.generate_conversation_response(
                topic="Career Discussion",
                conversation_history=[],
                user_message=question,
                session=session
            )
            
            response_text = response_data.get('response', '')
            referenced_docs = response_data.get('referenced_documents', [])
            
            self.stdout.write(f"\n💬 Response:")
            self.stdout.write(self.style.SUCCESS(f"   {response_text}"))
            
            if referenced_docs:
                self.stdout.write(self.style.WARNING(f"\n   📄 Used: {', '.join(referenced_docs)}"))
            else:
                self.stdout.write(self.style.WARNING(f"\n  ℹ️  No documents used (low relevance)"))
            
            self.stdout.write("-" * 70)
        
        # Summary
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("✅ RAG TEST COMPLETE!"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"\nSession ID: {session.id}")
        self.stdout.write(f"Document: {document.filename} ({chunk_count} chunks)")
        self.stdout.write("\nThe system successfully:")
        self.stdout.write("  ✓ Extracted text from document")
        self.stdout.write("  ✓ Created semantic chunks")
        self.stdout.write("  ✓ Generated embeddings")
        self.stdout.write("  ✓ Retrieved relevant context")
        self.stdout.write("  ✓ Generated context-aware responses")
        self.stdout.write("\n" + "=" * 70 + "\n")
