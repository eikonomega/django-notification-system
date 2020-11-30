import logging
import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from ...models import Notification, UserTarget
from ...utils.notification_handlers import (
    send_email, send_push_message)
from website.database_apps.subject_manager.models import Subject

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Push all SCHEDULED notifications with a scheduled_delivery before the current date_time
    """

    help = __doc__

    def handle(self, *args, **options):
        # Get all SCHEDULED and RETRY notifications with a scheduled_delivery before the
        # current date_time for development team if env is not production.

        # Get all SCHEDULED and RETRY notifications with a
        # scheduled_delivery before the current date_time
        notifications = Notification.objects.filter(
            Q(status='SCHEDULED') | Q(status='RETRY'),
            scheduled_delivery__lte=timezone.now())

        if os.environ['ENVIRONMENT'] != 'production':
            notifications = notifications.filter(user_target__user__is_superuser=True)

        if getattr(settings, 'DISABLE_EMAILS', False):
            notifications = notifications.exclude(user_target__target__name='Email')

        # excludes all notifications where the user has OptOut object with has_opted_out=True
        notifications = notifications.exclude(user_target__user__notification_opt_out__has_opted_out=True)
        # Loop through each notification and attempt to push it
        for notification in notifications:
            print(f"{notification.user_target.user.username} - {notification.scheduled_delivery} - {notification.status}", file=self.stdout)
            print(f"{notification.title} - {notification.body}", file=self.stdout)
            if not notification.user_target.active:
                logger.debug('Tried to notify inactive target %s',  notification.user_target.target)
                notification.status = Notification.INACTIVE_DEVICE
                notification.save()
            elif notification.user_target.target.name == 'Expo':
                # Attempt to send push notifications to targets.
                response_message = send_push_message(notification)
                print(response_message, file=self.stdout)
                print('*********************************', file=self.stdout)
            elif notification.user_target.target.name == 'Email':
                # Attempt to send email notifications to targets.
                response_message = send_email(notification)
                print(response_message, file=self.stdout)
                print('*********************************', file=self.stdout)
            else:
                logger.debug(f'invalid notification target name {notification.user_target.target.name}')
