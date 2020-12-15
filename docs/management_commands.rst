Management Commands
==============================================

Alright friends, in additional to all the goodies we've already
talked about, we've got a couple of management commands to make 
your life easier. Like, a lot easier.

Process Notifications
---------------------
This is the big kahuna of the entire system. When run, this command 
will attempt to deliver all notifications with a status of `SCHEDULED` 
or `RETRY` whose ``scheduled_delivery`` attribute is anytime before the 
command was invoked.

How to Run it
+++++++++++++
.. parsed-literal::
        $ python manage.py process_notifications

Make Life Easy for Yourself
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Once you've ironed out any potential kinks in your system, 
consider setting up a CRON schedule for this command that runs
at an appropriate interval for your application. After that,
your notifications will fly off your database shelves to your
users without any further work on your end.

Important: If You Have Custom Notification Targets
++++++++++++++++++++++++++++++++++++++++++++++++++
If you have created custom notification targets, you MUST have 
created the appropriate handler modules. You can find about how 
to do this here. [JUSTIN: LINK TO EXTENDING PAGE.]

If this isn't done, no notifications for custom targets will be sent.

Example Usage
+++++++++++++

Creating Notifications
    .. code-block:: python   
        
        # First, we'll need to have some Notifications in our database 
        # in order for this command to send anything.
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        
        from django_notification_system.models import (
            TargetUserRecord, Notification)

        User = get_user_model()
        
        user = User.objects.get(first_name="Eggs", last_name="Benedict")

        # Let's assume this user has 3 TargetUserRecord objects, 
        # one for Expo, one for Twilio and one for Email.
        user_targets = TargetUserRecord.objects.filter(
            user=user)

        # We'll loop through these targets and create a basic notification 
        # instance for each one.
        for user_target in user_targets:
            Notification.objects.create(
                user_target=user_target,
                title=f"Test notification for {user.first_name} {user.last_name}",
                body="lorem ipsum...",
                status="SCHEDULED,
                scheduled_delivery=timezone.now()
            )

Now we have three Notifications ready to send. Let's run the command.

.. parsed-literal::
        $ python manage.py process_notifications


If all was successful, you will see the output below. What this means 
is that all Notifications (1) were sent and (2) have been updated 
to have a ``status`` of 'DELIVERED' and an ``attempted_delivery`` set 
to the time it was sent. 

.. parsed-literal::
        egg - 2020-12-06 19:57:38+00:00 - SCHEDULED
        Test notification for Eggs Benedict - lorem ipsum...
        SMS Successfully sent!
        *********************************
        egg - 2020-12-06 19:57:38+00:00 - SCHEDULED
        Test notification for Eggs Benedict - lorem ipsum...
        Email Successfully Sent
        *********************************
        egg - 2020-12-06 19:57:38+00:00 - SCHEDULED
        Test notification for Eggs Benedict - lorem ipsum...
        Notification Successfully Pushed!
        *********************************

If any error occurs, that will be captured in the output. 
Based on the ``retry`` attribute, the affected notification(s) 
will try sending the next time the command is invoked.


Create Email Target User Records
--------------------------------
The purpose of this command is to create an email target user record for each user
currently in your database or update them if they already exist. We do this by
inspecting the ``email`` attribute of the user object and creating/updating the 
corresponding notification system models as needed.

After initial installation of this package, we can see that the ``User Targets`` 
section of our admin panel is empty.

.. figure::  images/create_email_target_user_records/create_email_target_user_records_1.png
    :align:   center
    :scale: 25%

Oh no!

FEAR NOT! In your terminal, run the command:

.. parsed-literal::
        $ python manage.py create_email_target_user_records

After the command has been run, navigate to ``http://yoursite/admin/django_notification_system/usertarget/``.
You should see a newly created UserInNotificationTarget for each user currently 
in the DB.

.. figure::  images/create_email_target_user_records/create_email_target_user_records_2.png
    :align:   center
    :scale: 25%

These user targets are now available for all of your notification needs.


