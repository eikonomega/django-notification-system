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

        """
        # TODO: This isn't currently working, and we'll need to add in where we want them to keep
        # their handler functions
        import django_notification_system.notification_handlers
        handler_dir = path.dirname(inspect.getfile(
            django_notification_system.notification_handlers))
        for handle in os.listdir(path.join(handler_dir)):
            if '__init__' in handle:
                continue
            temp = {}
            try:
                handler = importlib.import_module(
                    f"django_notification_system.notification_handlers.{handle}")
                print(getattr(handler, 'send_notification'))
                temp['send_notification'] = getattr(handler, 'send_notification')
            except (ModuleNotFoundError, AttributeError):
                pass

            cls.__function_table[handle.partition('.py')[0]] = temp

    def handle(self, *args, **options):
        print(self._load_function_table())
        print(self.__function_table)
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
                pass
                # Dynamic imports....
                function = notification.user_target.target.name.lower()
                try:
                    response_message = self.__function_table[function]['send_notification'](
                        notification)
                except KeyError:
                    print(
                        f'invalid notification target name {notification.user_target.target.name}')
                else:
                    print(response_message)
                    print('*********************************')
