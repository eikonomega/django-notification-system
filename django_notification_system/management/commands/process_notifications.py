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
        handler_dir = path.dirname(
            inspect.getfile(django_notification_system.notification_handlers)
        )

        for file in os.listdir(path.join(handler_dir)):
            if "__init__" in file:
                # Ignore the init file
                continue
            try:
                # Strip off the .py before importing the module
                notification_system = file.partition(".py")[0]
                module = importlib.import_module(
                    f"django_notification_system.notification_handlers.{notification_system}"
                )
                print("Working Module", module.__dict__)
                # Add the function to our function table
                cls.__function_table[notification_system] = getattr(
                    module, "send_notification"
                )
            except (ModuleNotFoundError, AttributeError):
                pass

        print("After First Loopie Loop", cls.__function_table)

        for directory in settings.NOTIFICATION_SYSTEM_HANDLERS:
            for file in os.listdir(path.join(directory)):
                print("Current File Being Evaluated", file)
                if "__init__" in file:
                    # Ignore the init file
                    continue
                try:
                    module_spec = importlib.util.spec_from_file_location(
                        file, f"{directory}/{file}"
                    )
                    print("Module Spec:", module_spec)
                    module = importlib.util.module_from_spec(module_spec)
                    print("Module:", module)
                    module_spec.loader.exec_module(module)
                    real_func = getattr(module, "send_notification")

                    print("Function of Eggs, named Pepper", real_func)

                    notification_system = file.partition(".py")[0]
                    cls.__function_table[notification_system] = real_func

                    # Add the function to our function table
                    # cls.__function_table[notification_system] = real_func
                except (ModuleNotFoundError, AttributeError) as error:
                    print("FAILURE", error)
                    # print(getattr(module, "send_notification"))
                    pass

    def handle(self, *args, **options):
        # Load the function table
        self._load_function_table()
        print(self.__function_table)

        # Get all SCHEDULED and RETRY notifications with a
        # scheduled_delivery before the current date_time
        notifications = Notification.objects.filter(
            Q(status="SCHEDULED") | Q(status="RETRY"),
            scheduled_delivery__lte=timezone.now(),
        )

        # excludes all notifications where the user has OptOut object with has_opted_out=True
        notifications = notifications.exclude(
            user_target__user__notification_opt_out__active=True
        )

        # Loop through each notification and attempt to push it
        for notification in notifications:
            print(
                f"{notification.user_target.user.username} - {notification.scheduled_delivery} - {notification.status}"
            )
            print(f"{notification.title} - {notification.body}")

            if not notification.user_target.active:
                notification.status = Notification.INACTIVE_DEVICE
                notification.save()
            else:
                notification_type = (
                    notification.user_target.target.notification_module_name
                )
                try:
                    # Use our function table to call the appropriate sending function
                    response_message = self.__function_table[notification_type](
                        notification
                    )
                except KeyError:
                    print(
                        f"invalid notification target name {notification.user_target.target.name}"
                    )
                else:
                    # The notification was sent successfully
                    print(response_message)
                    print("*********************************")
