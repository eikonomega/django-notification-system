import importlib
import inspect
import os
from os import path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from ...models import Notification


class Command(BaseCommand):
    """
    Push all SCHEDULED notifications with a scheduled_delivery before the current date_time
    """

    help = __doc__

    __function_table = {}

    @classmethod
    def _load_function_table(cls):
        """
        This function will get our function table populated with all available `send_notification`
        functions.
        """
        import django_notification_system.notification_handlers
        # Get our handler directory. NOTE: We want to add one for the functions users will create
        # to add to our table.
        handler_dir = path.dirname(inspect.getfile(
            django_notification_system.notification_handlers))

        for handle in os.listdir(path.join(handler_dir)):
            if '__init__' in handle:
                # Ignore the init file
                continue
            try:
                # Strip off the .py before importing the module
                notification_system = handle.partition('.py')[0]
                handler = importlib.import_module(
                    f"django_notification_system.notification_handlers.{notification_system}")
                # Add the function to our function table
                cls.__function_table[notification_system] = getattr(handler, 'send_notification')
            except (ModuleNotFoundError, AttributeError):
                pass

    def handle(self, *args, **options):
        # Load the function table
        self._load_function_table()

        # Get all SCHEDULED and RETRY notifications with a
        # scheduled_delivery before the current date_time
        notifications = Notification.objects.filter(
            Q(status='SCHEDULED') | Q(status='RETRY'),
            scheduled_delivery__lte=timezone.now())

        # excludes all notifications where the user has OptOut object with has_opted_out=True
        notifications = notifications.exclude(
            user_target__user__notification_opt_out__active=True)

        # Loop through each notification and attempt to push it
        for notification in notifications:
            print(
                f"{notification.user_target.user.username} - {notification.scheduled_delivery} - {notification.status}")
            print(f"{notification.title} - {notification.body}")

            if not notification.user_target.active:
                notification.status = Notification.INACTIVE_DEVICE
                notification.save()
            else:
                notification_type = notification.user_target.target.name.lower()
                try:
                    # Use our function table to call the appropriate sending function
                    response_message = self.__function_table[notification_type](notification)
                except KeyError:
                    print(
                        f'invalid notification target name {notification.user_target.target.name}')
                else:
                    # The notification was sent successfully
                    print(response_message)
                    print('*********************************')
