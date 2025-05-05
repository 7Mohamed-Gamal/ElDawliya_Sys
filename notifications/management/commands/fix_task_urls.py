from django.core.management.base import BaseCommand
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Fix task URLs in notifications from /tasks/detail/ to /tasks/'

    def handle(self, *args, **options):
        # Get all notifications with URLs containing /tasks/detail/
        notifications = Notification.objects.filter(url__contains='/tasks/detail/')
        count = notifications.count()
        
        self.stdout.write(self.style.SUCCESS(f'Found {count} notifications with old task URLs'))
        
        # Update each notification
        for notification in notifications:
            old_url = notification.url
            task_id = old_url.split('/tasks/detail/')[1].strip('/')
            new_url = f'/tasks/{task_id}/'
            
            notification.url = new_url
            notification.save()
            
            self.stdout.write(f'Updated: {old_url} -> {new_url}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} notifications'))