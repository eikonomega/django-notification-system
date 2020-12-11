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

   <a href="https://github.com/crcresearch/django-notification-system/issues/" target="_blank">Github repo.</a>

Option 2: Writing custom notification creators and receivers.
-------------------------------------------------------------
**Example: Creating a New Notification Target**
        .. code-block:: python

                from django_notification_system.models import NotificationTarget

                # Note: The notification_module_name will be the name of the modules you will write
                # to support the new notification target. 
                # Example: if in my settings I have the NOTIFICATION_SYSTEM_HANDLERS = [BASE_DIR / "extra_handlers"],
                # and inside that directory I have a file called 'sms.py', the notification_module_name will be 'sms'
                target = NotificationTarget.objects.create(
                    name='SMS', 
                    notification_module_name='sms')

Option 3: Be a cool kid superstar. 
----------------------------------
Write your own custom stuff and submit a PR to share with others.