from django.core.management.base import BaseCommand
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Fix purchase request URLs in notifications from /purchase/requests/detail/ to /purchase/requests/'

    def handle(self, *args, **options):
        # Get all notifications with URLs containing /purchase/requests/detail/
        notifications = Notification.objects.filter(url__contains='/purchase/requests/detail/')
        count = notifications.count()
        
        self.stdout.write(self.style.SUCCESS(f'Found {count} notifications with old purchase request URLs'))
        
        # Update each notification
        for notification in notifications:
            old_url = notification.url
            request_id = old_url.split('/purchase/requests/detail/')[1].strip('/')
            new_url = f'/purchase/requests/{request_id}/'
            
            notification.url = new_url
            notification.save()
            
            self.stdout.write(f'Updated: {old_url} -> {new_url}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} notifications'))from django.core.management.base import BaseCommand
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Fix purchase request URLs in notifications from /purchase/requests/detail/ to /purchase/requests/'

    def handle(self, *args, **options):
        # Get all notifications with URLs containing /purchase/requests/detail/
        notifications = Notification.objects.filter(url__contains='/purchase/requests/detail/')
        count = notifications.count()
        
        self.stdout.write(self.style.SUCCESS(f'Found {count} notifications with old purchase request URLs'))
        
        # Update each notification
        for notification in notifications:
            old_url = notification.url
            request_id = old_url.split('/purchase/requests/detail/')[1].strip('/')
            new_url = f'/purchase/requests/{request_id}/'
            
            notification.url = new_url
            notification.save()
            
            self.stdout.write(f'Updated: {old_url} -> {new_url}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} notifications'))