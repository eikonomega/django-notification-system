Django Notification System Models
=================================
Target
------
A target represents something that can receive a notication from our system. Our system comes with 
three existing targets (Email, Twilio and Expo).

Attributes
++++++++++
======================== ======== =========================================================================================================================
**Key**                  **Type** **Description**
name                     str      The human friendly name for the target.
notification_module_name str      The name of the module in the notification_creators directory which will be used to create notifications for this target.
======================== ======== =========================================================================================================================

**Example Usage**
        .. code-block:: python

                from django_notification_system.models import NotificationTarget

                # Note: The notification_module_name will be the name of the module you have in the
                # directory you have specified in your settings file.
                # Example: if in my settings I have the NOTIFICATION_SYSTEM_HANDLERS = [BASE_DIR / "extra_handlers"],
                # and inside that directory I have a file called 'sms.py', the notification_module_name will be 'sms'
                target = NotificationTarget.objects.create(
                    name='SMS', 
                    notification_module_name='sms')
                
User Target
-----------
Each user will have a unique ID for each notification target, which is how we identify the individual 
who will receive the notification.

For example, for an email target, we need to store the user's email address.

Attributes
++++++++++
============== =========== ============================================================================================================
**Key**        **Type**    **Description**
user           Django User The User/Custom User instance associated with this record.
target         foreign key The associated target instance.
target_user_id str         The ID used in the target to uniquely identify the user.
description    str         A human friendly note about the user target.
active         boolean     Indicator of whether user target is active or not. For example, we have an outdated email record for a user.
============== =========== ============================================================================================================

**Example Usage**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model
                
                from django_notification_system.models import NotificationTarget, UserInNotificationTarget

                User = get_user_model()
                
                user = User.objects.get(first_name="Eggs", last_name="Benedict")
                target = NotificationTarget.objects.get(name='Twilio')
                
                user_target = UserInNotificationTarget.objects.create(
                    user=user,
                    target=target,
                    target_user_id=user.phone_number,
                    description=f"{user.first_name} {user.last_name}'s Twilio",
                    active=True
                )

**Class method**

There is a ``reset_email_target`` method that can be used on this model. This will either create an email
UserInNotificationTarget for this User or update their email UserInNotificationTarget if the User email has been updated.

**Example Usage**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model
                
                from django_notification_system.models import UserInNotificationTarget

                User = get_user_model()
                
                user = User.objects.get(first_name="Eggs", last_name="Benedict")
                user.email = 'egg@egg.egg'
                user.save()

                new_user_target = UserInNotificationTarget.reset_email_target(user)


NotificationOptOut
------
Users who have opted-out of communications will have an instance of this model.

Attributes
++++++++++
======= =========== ==========================================================
**Key** **Type**    **Description**
user    Django User The User/Custom User instance associated with this record.
active  boolean     Indicator for whether the opt out is active or not.
======= =========== ==========================================================

**Example Usage**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model
                
                from django_notification_system.models import NotificationOptOut

                User = get_user_model()
                user = User.objects.get(first_name="Eggs", last_name="Benedict")
                
                opt_out = NotificationOptOut.objects.create(
                    user=user,
                    active=True)

**Note**

When an instance of this model is saved, if the opt out is active change the status of notifications 
with a current status of SCHEDULED or RETRY to OPTED_OUT.

Notification
------------
A Notification is a representation of a notification in the database.

Attributes
++++++++++
=================== =========== =================================================================================================================
**Key**             **Type**    **Description**
user_target         UserInNotificationTarget  The UserInNotificationTarget associated with notification
title               str         The title for the notification. Exact representation depends on the target.
body                str         The main message of the notification to be sent.
extra               dict        A dictionary of extra data to be sent to the notification processor. Valid keys are determined by each processor.
status              str         The status of Notification. Options are: 'SCHEDULED', 'DELIVERED', 'DELIVERY_FAILURE', 'RETRY', 'INACTIVE_DEVICE'
scheduled_delivery  DateTime    Day and time Notification is to be sent.
attempted_delivery  DateTime    Day and time attempted to deliver Notification.
retry_time_interval PositiveInt If a notification fails, this is the amount of time to wait until retrying to send it.
retry_attempts      PositiveInt The number of retries that have been attempted.
max_retries         PositiveInt The max number of allowed retries.
=================== =========== =================================================================================================================

**Example Usage**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model
                from django.utils import timezone
                
                from django_notification_system.models import UserInNotificationTarget, Notification

                User = get_user_model()
                user = User.objects.get(first_name="Eggs", last_name="Benedict")

                userTarget = UserInNotificationTarget.objects.get(
                        user=User,
                        target__name='Email')
                
                # extra defaults to {}
                # retry_time_interval defaults to 0
                # retry_attempts defaults to 0
                # max_retries defaults to 3
                notification = Notification.objects.create(
                        user_target=user_target,
                        title=f"Good morning, {user.first_name}",
                        body="lorem ipsum...",
                        status="SCHEDULED",
                        scheduled_delivery=timezone.now()
                )

**Note**

We perform a few data checks whenever an instance is saved.

        1. Don't allow notifications with an attempted delivery date to
           have a status of 'SCHEDULED'.
        2. If a notification has a status other than 'SCHEDULED' it MUST
           have an attempted delivery date.
        3. Don't allow notifications to be saved if the user has opted out.