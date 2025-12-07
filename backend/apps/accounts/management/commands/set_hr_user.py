from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class Command(BaseCommand):
    help = 'Adds or removes a user from the HR group'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('--remove', action='store_true', help='Remove from HR group instead of adding')

    def handle(self, *args, **options):
        username = options['username']
        remove = options['remove']

        try:
            user = User.objects.get(username=username)
            hr_group, created = Group.objects.get_or_create(name='HR')
            
            if created:
                self.stdout.write(self.style.WARNING('Created new group "HR"'))

            if remove:
                user.groups.remove(hr_group)
                action = "removed from"
            else:
                user.groups.add(hr_group)
                action = "added to"
            
            self.stdout.write(self.style.SUCCESS(f'Successfully {action} HR group: {username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
