from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.interviews.models import Interview, InterviewQuestion
from apps.questions.models import Question, QuestionCategory
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample interview data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding interview data...')

        # Create question categories if they don't exist
        categories = {
            'technical': QuestionCategory.objects.get_or_create(
                name='Technical',
                defaults={'description': 'Technical interview questions'}
            )[0],
            'behavioral': QuestionCategory.objects.get_or_create(
                name='Behavioral',
                defaults={'description': 'Behavioral interview questions'}
            )[0],
        }

        # Create sample questions for different position types
        questions_data = [
            {'text': 'Tell me about yourself and your background.', 'category': 'behavioral', 'position_type': 'software_engineer', 'difficulty': 'easy'},
            {'text': 'What is your experience with Python and Django?', 'category': 'technical', 'position_type': 'software_engineer', 'difficulty': 'medium'},
            {'text': 'Explain the difference between a class and an instance.', 'category': 'technical', 'position_type': 'software_engineer', 'difficulty': 'medium'},
            {'text': 'Describe a challenging project you worked on.', 'category': 'behavioral', 'position_type': 'software_engineer', 'difficulty': 'medium'},
            {'text': 'How do you handle tight deadlines?', 'category': 'behavioral', 'position_type': 'product_manager', 'difficulty': 'easy'},
            {'text': 'What is your product management philosophy?', 'category': 'behavioral', 'position_type': 'product_manager', 'difficulty': 'medium'},
        ]

        for q_data in questions_data:
            Question.objects.get_or_create(
                text=q_data['text'],
                defaults={
                    'category': categories[q_data['category']],
                    'position_type': q_data['position_type'],
                    'difficulty': q_data['difficulty'],
                }
            )

        # Create sample applicants
        applicants_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'bob_wilson', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Wilson'},
            {'username': 'alice_brown', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Brown'},
        ]

        applicants = []
        for app_data in applicants_data:
            user, created = User.objects.get_or_create(
                username=app_data['username'],
                defaults={
                    'email': app_data['email'],
                    'first_name': app_data['first_name'],
                    'last_name': app_data['last_name'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            applicants.append(user)

        # Create sample interviews
        position_types = ['software_engineer', 'product_manager', 'data_scientist']
        statuses = ['pending', 'in_progress', 'completed', 'evaluated']

        for i, applicant in enumerate(applicants):
            position_type = position_types[i % len(position_types)]
            status = statuses[i % len(statuses)]
            
            # Create interview
            interview = Interview.objects.create(
                applicant=applicant,
                position_type=position_type,
                status=status,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )

            # Get questions for this position type
            position_questions = Question.objects.filter(position_type=position_type)[:3]

            # Create interview questions
            for idx, question in enumerate(position_questions):
                InterviewQuestion.objects.create(
                    interview=interview,
                    question=question,
                    order=idx + 1,
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded interview data!'))
        self.stdout.write(f'Created {len(applicants)} applicants')
        self.stdout.write(f'Created {Interview.objects.count()} interviews')
        self.stdout.write(f'Created {InterviewQuestion.objects.count()} interview questions')
