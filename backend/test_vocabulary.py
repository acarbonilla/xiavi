import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model
from apps.learning.models import VocabularyItem
from apps.conversations.models import ConversationSession

User = get_user_model()

# Get or create a test user
try:
    user = User.objects.get(username='testuser')
except User.DoesNotExist:
    user = User.objects.create(username='testuser', email='test@example.com')

# Create a mock session
session = ConversationSession.objects.create(user=user)

# Mock feedback data with vocabulary
feedback_data = {
    'suggested_vocabulary': [
        {
            'word': 'serendipity',
            'definition': 'the occurrence and development of events by chance in a happy or beneficial way',
            'example': 'It was pure serendipity that we met at the coffee shop.',
            'translation': 'serendipia'
        },
        {
            'word': 'ephemeral',
            'definition': 'lasting for a very short time',
            'example': 'The beauty of the sunset was ephemeral.',
            'translation': 'efímero'
        }
    ]
}

# Simulate the logic in the view
print("Simulating vocabulary creation...")
suggested_vocab = feedback_data.get('suggested_vocabulary', [])
if suggested_vocab:
    for item in suggested_vocab:
        try:
            vocab_item, created = VocabularyItem.objects.get_or_create(
                user=user,
                word=item['word'],
                defaults={
                    'definition': item['definition'],
                    'example_sentence': item.get('example', ''),
                    'translation': item.get('translation', ''),
                    'source_session': session
                }
            )
            action = "Created" if created else "Retrieved"
            print(f"{action} item: {vocab_item.word}")
            print(f"  Definition: {vocab_item.definition}")
            print(f"  Example: {vocab_item.example_sentence}")
        except Exception as e:
            print(f"Error saving vocabulary item {item.get('word')}: {e}")

# Verify items in database
print("\nVerifying database content:")
items = VocabularyItem.objects.filter(user=user)
print(f"Found {items.count()} vocabulary items for user {user.username}:")
for item in items:
    print(f"- {item.word}: {item.definition[:50]}...")

# Clean up
print("\nCleaning up...")
items.delete()
session.delete()
print("Done.")
