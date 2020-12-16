Installation
=================================

Requirements
----------------------------------
* Python 3. Yes, we have completely ignored Python 2. Sad face.
* Django 3+
* A computer... preferrably plugged in.

Excuse me sir, may I have another?
----------------------------------
Only the nerdiest of nerds put Dickens puns in their installation docs.

`pip install django-notification-system`

Post-Install Setup
----------------------------------
Make the following additions to your Django settings.

**Django Settings Additions**
        .. code-block:: python

                # You will need to add email information as specified here: https://docs.djangoproject.com/en/3.1/topics/email/
                # This can include:
                EMAIL_HOST = ''
                EMAIL_PORT = ''
                EMAIL_HOST_USER = ''
                EMAIL_HOST_PASSWORD = ''
                # and the EMAIL_USE_TLS and EMAIL_USE_SSL settings control whether a secure connection is used.
                
                # Add the package to your installed apps.
                INSTALLED_APPS = [
                    "django_notification_system",
                    ...
                ]

                # Twilio Required settings, if you're not planning on using Twilio 
                # these can be set to empty strings
                NOTIFICATION_SYSTEM_TARGETS={
                  # Twilio Required settings, if you're not planning on using Twilio these can be set
                  # to empty strings
                  "twilio_sms": {
                      'account_sid': '',
                      'auth_token': '',
                      'sender': '' # This is the phone number associated with the Twilio account
                  },
                  "email": {
                      'from_email': '' # Sending email address
                  }
                }


If you would like to add support for addition types of notifications that don't exist in the package yet, 
you'll need to add some additional items to your Django settings. This is only necessary if you are planning on 
:doc:`extending the system <../extending>`.


