from django.core.management.base import BaseCommand
from apps.conversations.models import ConversationSession
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Clean up active/incomplete sessions with no messages or mark them as completed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to clean up sessions for (optional)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        dry_run = options.get('dry_run', False)

        # Filter sessions
        sessions = ConversationSession.objects.filter(
            status__in=['active', 'incomplete']
        )
        
        if user_id:
            sessions = sessions.filter(user_id=user_id)

        self.stdout.write(f"\nFound {sessions.count()} active/incomplete sessions\n")

        for session in sessions:
            topic_name = session.topic.name if session.topic else "No Topic"
            self.stdout.write(
                f"Session {session.id}: {topic_name} "
                f"(Status: {session.status}, Messages: {session.message_count}, "
                f"User: {session.user.username})"
            )

            # If session has no messages, delete it
            if session.message_count == 0:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f"  → Would DELETE (no messages)")
                    )
                else:
                    session.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f"  → DELETED (no messages)")
                    )
            # If session has messages but is old (more than 24 hours), mark as incomplete
            else:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f"  → Would keep as {session.status}")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"  → Keeping as {session.status}")
                    )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n✓ Dry run complete. Use without --dry-run to apply changes.\n")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\n✓ Cleanup complete!\n")
            )
