Built-In Notification Creators & Handlers
============================================

What allows for a given notification type to be supported is the existence of a 
**notification creator** and **notification handler** functions. Their jobs are to:

    1. Create a ``Notification`` record for a given notification target. 
    2. Interpret a ``Notification`` record in an appropriate way for a given target and actually send the notification.

Currently there are 3 different types of notifications with built-in support:

    * Email
    * Twilio SMS
    * Expo Push

Natively Supported Notification Targets
---------------------------------------

Email Notifications
+++++++++++++++++++

Notification Creator
####################

**Example: Email Notification Creator**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model

                from django_notification_system.notification_creators.email import create_notification

                User = get_user_model()

                user = User.objects.get(first_name="Eggs", last_name="Benedict")

                # Note how the extra parameter is used here.
                # See function parameters below for more details.
                create_notification(
                    user=user,
                    title='Cool Email',
                    extra={
                        "user": user,
                        "date": "12-07-2020"
                        "template_name": "templates/eggs_email.html" 
                    })

**Function Parameters**
    =================== ================== =========================================================
    **Key**             **Type**           **Description**
    user                Django User        The user to whom the notification will be sent.
    title               str                The title for the notification.
    body                str                Body of the email. Defaults to a blank string if 
                                           not given. Additionally, if this parameter is not 
                                           specific AND "template_name" is present in `extra`,                                            
                                           an attempt will be made to generate the body from 
                                           that template.
    
    scheduled_delivery  datetime(optional) When to delivery the notification. Defaults to 
                                           immediately.
    
    retry_time_interval int(optional)      When to retry sending the notification if a delivery
                                           failure occurs. Defaults to 1440 seconds.
    
    max_retries         int(optional)      Maximum number of retry attempts. 
                                           Defaults to 3.
    
    quiet               bool(optional)     Suppress exceptions from being raised. 
                                           Defaults to False.
    
    extra               dict(optional)     User specified additional data that will be used 
                                           to populate an HTML template if 
                                           "template_name" is present inside.
    =================== ================== =========================================================

The above example will create a Notification with the following values:

.. figure::  images/utility_functions/create_email_notification.png
    :align:   center
    :scale: 25%

Notification Handler
####################

**Example Usage**
        .. code-block:: python
                
                from django.utils import timezone

                from django_notification_system.models import Notification
                from django_notification_system.notification_handlers.email import send_notification
                
                # Get all email notifications.
                notifications_to_send = Notification.objects.filter(
                    target_user_record__target__name='Email',
                    status='SCHEDULED',
                    scheduled_delivery__lte=timezone.now())
                
                # Send each email notification to the handler.
                for notification in notifications_to_send:
                    send_notification(notification)

Expo Push Notifications
+++++++++++++++++++++++

Notification Creator
####################

**Example: Expo Notification Creator**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model

                from django_notification_system.notification_creators.expo import create_notification

                User = get_user_model()

                user = User.objects.get(first_name="Eggs", last_name="Benedict")

                create_notification(
                    user=user,
                    title=f"Hello {user.first_name}",
                    body="Test push notification")

**Parameters**
    =================== ================== =========================================================
    **Key**             **Type**           **Description**
    user                Django User        The user to whom the notification will be sent.
    title               str                The title for the push notification.
    body                str                The body of the push notification.
    scheduled_delivery  datetime(optional) When to delivery the notification. Defaults to 
                                           immediately.
    
    retry_time_interval int(optional)      Delay between send attempts. Defaults to 60 seconds.
    max_retries         int(optional)      Maximum number of retry attempts. 
                                           Defaults to 3.
    
    quiet               bool(optional)     Suppress exceptions from being raised. 
                                           Defaults to False.
    
    extra               dict(optional)     Defaults to None.
    =================== ================== =========================================================

The above example will create a Notification with the following values:

.. figure::  images/utility_functions/create_expo_notification.png
    :align:   center
    :scale: 25%

Notification Handler
####################

**Example Usage**
        .. code-block:: python
                
                from django.utils import timezone

                from django_notification_system.models import Notification
                from django_notification_system.notification_handlers.expo import send_notification

                # Get all Expo notifications.
                notifications_to_send = Notification.objects.filter(
                    target_user_record__target__name='Expo',
                    status='SCHEDULED',
                    scheduled_delivery__lte=timezone.now())
                
                # Send each Expo notification to the handler.
                for notification in notifications_to_send:
                    send_notification(notification)

Twilio SMS
++++++++++

Notification Creator
####################

**Example: Twilio SMS Notification Creator**
        .. code-block:: python
                
                from django.contrib.auth import get_user_model

                from django_notification_system.notification_creators.twilio import create_notification

                User = get_user_model()

                user = User.objects.get(first_name="Eggs", last_name="Benedict")

                create_notification(
                    user=user,
                    title=f"Hello {user.first_name}",
                    body="Test sms notification")

**Parameters**
    =================== ================== =========================================================
    **Key**             **Type**           **Description**
    user                Django User        The user to whom the notification will be sent.
    title               str                The title for the sms notification.
    body                str                The body of the sms notification.
    scheduled_delivery  datetime(optional) When to deliver the notification. Defaults to 
                                           immediately.
    
    retry_time_interval int(optional)      Delay between send attempts. Defaults to 60 seconds.
    max_retries         int(optional)      Maximum number of retry attempts. 
                                           Defaults to 3.
    
    quiet               bool(optional)     Suppress exceptions from being raised. 
                                           Defaults to False.
    
    extra               dict(optional)     Defaults to None.
    =================== ================== =========================================================



The above example will create a Notification with the following values:

.. figure::  images/utility_functions/create_twilio_notification.png
    :align:   center
    :scale: 25%

Notification Handler
####################

**Example Usage**
        .. code-block:: python
                
                from django.utils import timezone

                from django_notification_system.models import Notification
                from django_notification_system.notification_handlers.twilio import send_notification

                # Get all notifications for Twilio target.
                notifications_to_send = Notification.objects.filter(
                    target_user_record__target__name='Twilio',
                    status='SCHEDULED',
                    scheduled_delivery__lte=timezone.now())
                
                # Send each notification to the Twilio handler.
                for notification in notifications_to_send:
                    send_notification(notification)