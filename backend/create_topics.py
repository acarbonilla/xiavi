from apps.conversations.models import Topic

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
    Topic.objects.get_or_create(name=topic_data['name'], defaults=topic_data)

print("✅ Topics created successfully!")
