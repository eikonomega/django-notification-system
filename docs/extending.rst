Adding Support for Custom Notification Targets
==============================================

Option 1: Beg us to do it.
--------------------------
In terms of easy to do, this would be at the top of the list. However, we've got to be 
honest. We're crazy busy usually, so the chances that we will be able to do this aren't
great. However, if we see a request that we think would have a lot of mileage in it we 
may take it up.

If you want to try this method, just submit an issue on the |github_repo|

.. |github_repo| raw:: html

   <a href="https://github.com/crcresearch/django-notification-system/" target="_blank">Github repo.</a>

Option 2: Add Support Yourself
-------------------------------------------------------------
Ok, you can do this! It's actually pretty easy. Here is the big picture.
Let's go through it step by step.

Step 1: Add Required Django Settings
++++++++++++++++++++++++++++++++++++

The first step is to tell Django where to look for custom notification creators and handlers.
Here is how you do that.

**Django Settings Additions**
        .. code-block:: python

                # A list of locations for the system to search for notification creators. 
                # For each location listed, each module will be searched for a `create_notification` function.
                NOTIFICATION_SYSTEM_CREATORS = [
                    '/path/to/creator_modules', 
                    '/another/path/to/creator_modules']
                    
                # A list of locations for the system to search for notification handlers. 
                # For each location listed, each module will be searched for a `send_notification` function.
                NOTIFICATION_SYSTEM_HANDLERS = [
                    '/path/to/handler_modules', 
                    '/another/path/to/handler_modules']
                
Step 2: Create the Notification Target
++++++++++++++++++++++++++++++++++++++

Now that you've added the required Django settings, we need to create a ``NotificationTarget`` object
for your custom target.
        
**Example: Creating a New Notification Target**
        .. code-block:: python

                from django_notification_system.models import NotificationTarget

                # Note: The notification_module_name will be the name of the modules you will write
                # to support the new notification target. 
                # Example: If in my settings I have the NOTIFICATION_SYSTEM_HANDLERS = ["/path/to/extra_handlers"],
                # and inside that directory I have a file called 'carrier_pigeon.py', the notification_module_name should be 'carrier_pigeon'
                target = NotificationTarget.objects.create(
                    name='Carrier Pigeon', 
                    notification_module_name='carrier_pigeon')

Step 2: Add a Notification Creator
++++++++++++++++++++++++++++++++++

Next, we need to create the corresponding creator and handler functions.
We'll start with the handler function.

In the example above, you created a ``NotificationTarget`` and set it's ``notification_module_name`` to ``carrier_pigeon``. 
This means that the ``process_notifications`` management command is going to look for modules named ``carrier_pigeon`` in the paths
specified by your Django settings additions to find the necessary creator and handler functions.

Let's start by writing our creator function.

**Example: Creating the Carrier Pigeon Notification Creator**
        .. code-block:: python

            # /path/to/creators/carrier_pigeon.py
                
            from datetime import datetime
            from django.utils import timezone
            from django.contrib.auth import get_user_model
                
            # Some common exceptions you might want to use.
            from django_notification_system.exceptions import (
                NotificationsNotCreated,
                UserHasNoTargets,
                UserIsOptedOut,
            )

            # A utility function to see if the user has an opt-out.
            from django_notification_system.utils import (
                check_for_user_opt_out
            )
                
            from ..models import Notification, TargetUserRecord

            # NOTE: The function MUST be named `create_notification`
            def create_notification(
                user: 'Django User',
                title: str,
                body: str,
                scheduled_delivery: datetime = None,
                retry_time_interval: int = 60,
                max_retries: int = 3,
                quiet=False,
                extra: dict = None,
            ) -> None:
                """
                Create a Carrier Pigeon notification.

                Args:
                    user (User): The user to whom the notification will be sent.
                    title (str): The title for the notification.
                    body (str): The body of the notification.
                    scheduled_delivery (datetime, optional): Defaults to immediately.
                    retry_time_interval (int, optional): Delay between send attempts. Defaults to 60 seconds.
                    max_retries (int, optional): Maximum number of retry attempts for delivery. Defaults to 3.
                    quiet (bool, optional): Suppress exceptions from being raised. Defaults to False.
                    extra (dict, optional): Defaults to None.

                Raises:
                    UserIsOptedOut: When the user has an active opt-out.
                    UserHasNoTargets: When the user has no eligible targets for this notification type.
                    NotificationsNotCreated: When the notifications could not be created.
                """

                # Check if user is opted-out.
                try:
                    check_for_user_opt_out(user=user)
                except UserIsOptedOut:
                    if quiet:
                        return
                    else:
                        raise UserIsOptedOut()

                # Grab all active TargetUserRecords in the Carrier Pigeon target 
                # the user has. You NEVER KNOW if they might have more than one pigeon.
                carrier_pigeon_user_records = TargetUserRecord.objects.filter(
                    user=user,
                    target__name="Carrier Pigeon",
                    active=True,
                )
                
                # If the user has no active carrier pigions, we
                # can't create any notifications for them.
                if not carrier_pigeon_user_records:
                    if quiet:
                        return
                    else:
                        raise UserHasNoTargets()

                # Provide a default scheduled delivery if none is provided.
                if scheduled_delivery is None:
                        scheduled_delivery = timezone.now()

                notifications_created = []
                for record in carrier_pigeon_user_records:
                    
                    if extra is None:
                        extra = {}  

                    # Create notifications while taking some precautions
                    # not to duplicate ones that are already there.
                    notification, created = Notification.objects.get_or_create(
                        target_user_record=record,
                        title=title,
                        scheduled_delivery=scheduled_delivery,
                        extra=extra,
                        defaults={
                                "body": body,
                                "status": "SCHEDULED",
                                "retry_time_interval": retry_time_interval,
                                "max_retries": max_retries,
                            },
                        )

                    # If a new notification was created, add it to the list.
                    if created:
                        notifications_created.append(notification)

                # If no notifications were created, possibly raise an exception.
                if not notifications_created:
                    if quiet:
                        return
                    else:
                        raise NotificationsNotCreated()


Step 3: Add a Notification Handler
++++++++++++++++++++++++++++++++++

Alright my friend, last step. The final thing you need to do is write a 
notification handler. These are used by the `process_notifications` management
command to actual send the notifications to the various targets.

For the sake of illustration, we'll continue with our carrier pigeon example.

**Example: Creating the Carrier Pigeon Notification Handler**
    .. code-block:: python

        # /path/to/hanlders/carrier_pigeon.py

        from dateutil.relativedelta import relativedelta
        from django.utils import timezone

        # Usually, the notification provider will have either an
        # existing Python SDK or RestFUL API which your handler 
        # will need to interact with.
        from carrior_pigeon_sdk import (
            request_delivery,
            request_priority_delivery,
            request_economy_aka_old_pigeon_delivery
            PigeonDiedException,
            PigeonGotLostException
        )

        from ..utils import check_and_update_retry_attempts

        # You MUST have a function called send_notification in this module.
        def send_notification(notification) -> str:
            """
            Send a notification to the carrior pigeon service for delivery.

            Args:
                notification (Notification): The notification to be delivery by carrior pigeon.

            Returns:
                str: Whether the push notification has successfully sent, or an error message.
            """
            try:
                # Invoke whatever method of the target service you need to.
                # Notice how the handler is responsible to translate data
                # from the `Notification` record to what is needed by the service.
                response = request_delivery(
                    recipient=notification.target_user_record.target_user_id,
                    sender="My Cool App",
                    title=notification.title,
                    body=notification.body,
                    talking_pigeon=True if "speak_message" in test and extra["speak_message"] else False,
                    pay_on_delivery=True if "cheapskate" in test and extra["cheapskate"] else False
                )

            except PigeonDiedException as error:  
                # Probably not going to be able to reattempt delivery.
                notification.attempted_delivery = timezone.now()
                notification.status = notification.DELIVERY_FAILURE
                notification.save()

                # This string will be displayed by the 
                # `process_notifications` management command.
                return "Yeah, so, your pigeon died. Wah wah."

            except PigeonGotLostException as error:  
                notification.attempted_delivery = timezone.now()
                
                # In this case, it is possible to attempt another delivery.
                # BUT, we should check if the max attempts have been made.
                if notification.retry_attempts < notification.max_retries:
                    notification.status = notification.RETRY
                    notification.scheduled_delivery = timezone.now() + relativedelta(
                        minutes=notification.retry_time_interval)
                    notification.save()
                    return "Your bird got lost, but we'll give it another try later."
                else:
                    notification.status = notification.DELIVERY_FAILURE
                    notification.save()
                    return "Your bird got really dumb and keeps getting lost. And it ate your message."


Option 3: Be a cool kid superstar. 
----------------------------------
Write your own custom stuff and submit a PR to share with others.