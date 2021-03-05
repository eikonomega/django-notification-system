import importlib
import inspect
import os
from os import path

from django.db.models import Q
from django.utils import timezone
from django.conf import settings
if settings.NOTIFICATION_SYSTEM_USE_CELERY:
    from celery.execute import send_task

from ..models import Notification
from ..notification_handlers.email import send_notification as send_email
from ..notification_handlers.twilio import send_notification as send_twilio
from ..notification_handlers.expo import send_notification as send_expo


class Sender():
    __function_table = {
        "expo": send_expo,
        "twilio": send_twilio,
        "email": send_email
    }

    def __init__(self, *args, **kwargs):
        self._load_function_table()

    @classmethod
    def _load_function_table(cls):
        """
        This function will get our function table populated with all available `send_notification`
        functions.
        """
        for directory in settings.NOTIFICATION_SYSTEM_HANDLERS:
            try:
                for file in os.listdir(path.join(directory)):
                    if "__init__" in file:
                        # Ignore the init file
                        continue
                    try:
                        # Create the module spec
                        module_spec = importlib.util.spec_from_file_location(
                            file, f"{directory}/{file}")
                        # Create a new module  based  on the spec
                        module = importlib.util.module_from_spec(module_spec)
                        # An abstract method that executes the module
                        module_spec.loader.exec_module(module)
                        #  Get the actual function
                        real_func = getattr(module, "send_notification")
                        # Add it to our dictionary of functions
                        notification_system = file.partition(".py")[0]
                        cls.__function_table[notification_system] = real_func
                    except (ModuleNotFoundError, AttributeError):
                        pass
            except FileNotFoundError:
                # the directory provided in the settings file does not exist
                pass

    @classmethod
    def send_async(cls, notification_type, notification_id):
        sender = Sender()
        notification = Notification.objects.get(id=notification_id)
        sender.send_notification(notification_type, notification)


    def send_notification(self, notification_type, notification):
        return self.__function_table[notification_type](notification)

    def execute(self, verbose=False):
        # Get all SCHEDULED and RETRY notifications with a
        # scheduled_delivery before the current date_time
        notifications = Notification.objects.filter(
            Q(status="SCHEDULED") | Q(status="RETRY"),
            scheduled_delivery__lte=timezone.now(),
        )

        # excludes all notifications where the user has NotificationOptOut object with has_opted_out=True
        notifications = notifications.exclude(target_user_record__user__notification_opt_out__active=True)

        # Loop through each notification and attempt to push it
        for notification in notifications:
            if verbose:
                print(
                    f"{notification.target_user_record.user.username} - {notification.scheduled_delivery} - {notification.status}")
                print(f"{notification.title} - {notification.body}")

            if not notification.target_user_record.active:
                notification.status = Notification.INACTIVE_DEVICE
                notification.save()
            else:
                notification_type = (
                    notification.target_user_record.target.notification_module_name
                )
                try:
                    # Use our function table to call the appropriate sending function
                    if settings.NOTIFICATION_SYSTEM_USE_CELERY:
                        notification.status = "ASYNCED"
                        notification.save()
                        send_task("Sender.send_async", [notification_type, notification.id])
                    else:
                        response_message = self.send_notification(notification_type, notification)
                except KeyError:
                    if verbose:
                        print(
                            f"invalid notification target name {notification.target_user_record.target.name}")
                elif verbose:
                    # The notification was sent successfully
                    print(response_message)
                    print("*********************************")
