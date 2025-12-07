# Generated migration to populate default voice for existing profiles

from django.db import migrations


def populate_default_voice(apps, schema_editor):
    """Set default voice for existing learner profiles."""
    LearnerProfile = apps.get_model('accounts', 'LearnerProfile')
    
    # Update all profiles that don't have a voice preference set
    updated_count = LearnerProfile.objects.filter(
        preferred_voice__isnull=True
    ).update(preferred_voice='warm_friendly')
    
    print(f"Updated {updated_count} learner profiles with default voice")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_add_preferred_voice'),
    ]

    operations = [
        migrations.RunPython(populate_default_voice, reverse_code=migrations.RunPython.noop),
    ]
