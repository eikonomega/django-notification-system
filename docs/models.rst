Django Notification System Models
=================================
There are 4 models that the library will install in your application.

Notification Target
------
A notification target represents something that can receive a notication from our system. 
In this release of the package, we natively support Email, Twilio and Expo (push notifications) targets.

Unless you are (JUSTIN: Link to extending the system ) you won't need to create any targets
that are not already pre-loaded during installation.

Attributes
++++++++++
======================== ======== =========================================================================================================================
**Key**                  **Type** **Description**
id                       uuid     Auto-generated record UUID. 
name                     str      The human friendly name for the target.
notification_module_name str      The name of the module in the NOTIFICATION_SYSTEM_CREATORS & NOTIFICATION_SYSTEM_HANDLERS 
                                  directories which will be used to create and process notifications for this target.
======================== ======== =========================================================================================================================

                
Target User Record
-----------
Each notification target will have an internal record for each of your users. For example, an email server would have a record
of all the valid email addresses that it supports. This model is used to tie a Django user in your database to it's representation 
in a given `NotificationTarget`.

For example, for the built-in email target, we need to store the user's email address on a `TargetUserRecord` instance so that
when we can the email `NotificationTarget` the correct address to send email notifications to for a given user.

Attributes
++++++++++
============== =========== ===============================================================================================================
**Key**        **Type**    **Description**
id             uuid        Auto-generated record UUID. 
user           Django User The Django user instance associated with this record.
target         foreign key The associated notification target instance.
target_user_id str         The ID used in the target to uniquely identify the user.
description    str         A human friendly note about the user target.
active         boolean     Indicator of whether user target is active or not. For example, we may have an outdated email record for a user.
============== =========== ================================================================================================================

**Example Usage: Creating a Target User Record**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model
                
                from django_notification_system.models import NotificationTarget, TargetUserRecord

                # Let's assume for our example here that your user model has a `phone_number` attribute.
                User = get_user_model()
                
                user = User.objects.get(first_name="Eggs", last_name="Benedict")
                target = NotificationTarget.objects.get(name='Twilio')
                
                user_target = TargetUserRecord.objects.create(
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


Notification Opt Out
--------------------
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
=================== ======================== =================================================================================================================
**Key**             **Type**                 **Description**
user_target         UserInNotificationTarget The UserInNotificationTarget associated with notification
title               str                      The title for the notification. Exact representation depends on the target.
body                str                      The main message of the notification to be sent.
extra               dict                     A dictionary of extra data to be sent to the notification processor. Valid keys are determined by each processor.
status              str                      The status of Notification. Options are: 'SCHEDULED', 'DELIVERED', 'DELIVERY_FAILURE', 'RETRY', 'INACTIVE_DEVICE'
scheduled_delivery  DateTime                 Day and time Notification is to be sent.
attempted_delivery  DateTime                 Day and time attempted to deliver Notification.
retry_time_interval PositiveInt              If a notification fails, this is the amount of time to wait until retrying to send it.
retry_attempts      PositiveInt              The number of retries that have been attempted.
max_retries         PositiveInt              The max number of allowed retries.
=================== ======================== =================================================================================================================

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