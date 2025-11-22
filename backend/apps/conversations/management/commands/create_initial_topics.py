from django.core.management.base import BaseCommand
from apps.conversations.models import Topic

class Command(BaseCommand):
    help = 'Creates initial conversation topics'

    def handle(self, *args, **options):
        topics = [
            {
                "name": "Casual Chat",
                "description": "Everyday conversations about life, hobbies, and interests",
                "difficulty": "beginner",
                "icon": "message-circle",
                "color": "blue"
            },
            {
                "name": "Business Communication",
                "description": "Professional discussions, meetings, and presentations",
                "difficulty": "intermediate",
                "icon": "briefcase",
                "color": "purple"
            },
            {
                "name": "Academic Discussion",
                "description": "Intellectual conversations about science, history, and literature",
                "difficulty": "advanced",
                "icon": "book-open",
                "color": "green"
            },
            {
                "name": "Travel & Culture",
                "description": "Conversations about travel experiences and cultural topics",
                "difficulty": "beginner",
                "icon": "plane",
                "color": "orange"
            },
            {
                "name": "Current Events",
                "description": "Discuss news, trends, and current affairs",
                "difficulty": "intermediate",
                "icon": "newspaper",
                "color": "red"
            },
        ]

        for topic_data in topics:
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults=topic_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created topic: {topic.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Topic already exists: {topic.name}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully created all topics'))
