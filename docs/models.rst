Django Notification System Models
=================================
There are 4 models that the library will install in your application.

Notification Target
-------------------
A notification target represents something that can receive a notication from our system. 
In this release of the package, we natively support Email, Twilio and Expo (push notifications) targets.

Unless you are :doc:`extending the system <../extending>` you won't need to create any targets
that are not already pre-loaded during installation.

Attributes
++++++++++
======================== ======== ===============================================================
**Key**                  **Type** **Description**
id                       uuid     Auto-generated record UUID. 
name                     str      The human friendly name for the target.
notification_module_name str      The name of the module in the NOTIFICATION_SYSTEM_CREATORS & 
                                  NOTIFICATION_SYSTEM_HANDLERS directories which will be used to 
                                  create and process notifications for this target.
======================== ======== ===============================================================

                
Target User Record
------------------
Each notification target will have an internal record for each of your users. For example, 
an email server would have a record of all the valid email addresses that it supports. This 
model is used to tie a Django user in your database to it's representation in a given 
`NotificationTarget`.

For example, for the built-in email target, we need to store the user's email address on 
a `TargetUserRecord` instance so that when we can the email `NotificationTarget` the correct 
address to send email notifications to for a given user.

Attributes
++++++++++
============== =========== ================================================================================================================
**Key**        **Type**    **Description**
id             uuid        Auto-generated record UUID. 
user           Django User The Django user instance associated with this record.
target         foreign key The associated notification target instance.
target_user_id str         The ID used in the target to uniquely identify the user.
description    str         A human friendly note about the user target.
active         boolean     Indicator of whether user target is active or not. For example, 
                           we may have an outdated email record for a user.
============== =========== ================================================================================================================

**Example: Creating a Target User Record**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model
                from django_notification_system.models import (
                    NotificationTarget, TargetUserRecord)

                # Let's assume for our example here that your user model has a `phone_number` attribute.
                User = get_user_model()
                
                user = User.objects.get(first_name="Eggs", last_name="Benedict")
                target = NotificationTarget.objects.get(name='Twilio')
                
                # Create a target user record.
                target_user_record = TargetUserRecord.objects.create(
                    user=user,
                    target=target,
                    target_user_id=user.phone_number,
                    description=f"{user.first_name} {user.last_name}'s Twilio",
                    active=True
                )


Notification Opt Out
--------------------
Use this model to track whether or not users have opted-out of receiving 
notifications from you. 

  * For the built in `Process Notifications` command, we ensure that 
    notifications are not sent to users with active opt-outs.
  * Make sure to check this yourself if you implement other ways of
    sending notifications or you may find yourself running afoul 
    of spam rules.

Attributes
++++++++++
======= =========== ==========================================================
**Key** **Type**    **Description**
user    Django User The Django user associated with this record.
active  boolean     Indicator for whether the opt out is active or not.
======= =========== ==========================================================

**Example: Creating an Opt out**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model
                from django_notification_system.models import NotificationOptOut

                User = get_user_model()
                user = User.objects.get(first_name="Eggs", last_name="Benedict")
                
                opt_out = NotificationOptOut.objects.create(
                    user=user,
                    active=True)

Unique Behavior
+++++++++++++++
When an instance of this model is saved, if the opt out is `active` 
existing notifications with a current status of SCHEDULED or RETRY 
will be changed to OPTED_OUT.

We do this to help prevent them from being sent, but also to keep
a record of what notifications had been scheduled before the user
opted-out.

Notification
------------
This model represents a notification in the database. SHOCKING!

Thus far, we've found this model to be flexible enough to handle 
any type of notification. Hopefully, you will find the same.

Core Concept
++++++++++++

Each type of notification target must have a corresponding handler module that
will process notifications that belong to that target. These handlers interpret 
the various attributes of a `Notification` instance to construct a valid
message for each target.

For each of the built-in targets, we have already written these handlers.
If you create additional targets, you'll need to write the corresponding handlers.
See the :doc:`extending the system <../extending>`  page for more information.

Attributes
++++++++++
=================== ======================== =================================================================================================================
**Key**             **Type**                 **Description**
target_user_record  TargetUserRecord         The TargetUserRecord associated with notification. This essentially 
                                             identifies the both the target (i.e. email) and the specific user in that 
                                             target (coolkid@nd.edu) that will receive the notification. 
title               str                      The title for the notification. 
body                str                      The main message of the notification to be sent.
extra               dict                     A dictionary of extra data to be sent to the notification handler. 
                                             Valid keys are determined by each handler.
status              str                      The status of Notification. Options are: 'SCHEDULED', 'DELIVERED', 
                                             'DELIVERY FAILURE', 'RETRY', 'INACTIVE DEVICE', 'OPTED OUT'
scheduled_delivery  DateTime                 Scheduled delivery date/time.
attempted_delivery  DateTime                 Last attempted delivery date/time.
retry_time_interval PositiveInt              If a notification delivery fails, this is the amount of time 
                                             to wait until retrying to send it.
retry_attempts      PositiveInt              The number of delivery retries that have been attempted.
max_retries         PositiveInt              The maximun number of allowed delivery attempts.
=================== ======================== =================================================================================================================

**Example: Creating an Email Notification**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model
                from django.utils import timezone
                
                from django_notification_system.models import UserInNotificationTarget, Notification

                # Get the user.
                User = get_user_model()
                user = User.objects.get(first_name="Eggs", last_name="Benedict")

                # The the user's target record for the email target.
                emailUserRecord = TargetUserRecord.objects.get(
                    user=User,
                    target__name='Email')
                
                # Create the notification instance. 
                # IMPORTANT: This does NOT send the notification, just schedules it.
                # See the docs on management commands for sending notifications.
                notification = Notification.objects.create(
                        user_target=user_target,
                        title=f"Good morning, {user.first_name}",
                        body="lorem ipsum...",
                        status="SCHEDULED",
                        scheduled_delivery=timezone.now()
                )

Unique Behavior
+++++++++++++++

We perform a few data checks whenever an notification instance is saved.

        1. You cannot set the status of notification to 'SCHEDULED' if you 
           also have an existing attempted delivery date.
        2. If a notification has a status other than 'SCHEDULED' or 'OPTED OUT it MUST
           have an attempted delivery date.
        3. Don't allow notifications to be saved if the user has opted out.