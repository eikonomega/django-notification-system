# [Django Notification System][docs]

[![pypi-version]][pypi]

**Finally, an awesome Django Notification System.**

Full documentation for the package is avalaible at https://django-notification-system.readthedocs.io/en/latest/

# Overview

Perhaps you've got a Django application that you'd like to send notifications from?

Well, we certainly have our share of them. And guess what? We're tired of writing code to create and send various
types of messages over and over again!

So, we've created this package to simplify things
a bit for future projects. Hopefully, it will help you too.

**Here's the stuff you get:**

1. A few Django models that are pretty important:

- `Notification`: A single notification. Flexible enough to handle many different types of notifications.
- `NotificationTarget`: A target for notifications. Email, SMS, etc.
- `TargetUserRecord`: Info about the user in a given target (Ex. Your "address" in the "email" target).
- `NotificationOptOut`: Single location to keep track of user opt outs. You don't want the spam police after you.

2. Built in support for [email, Twilio SMS, and Expo push notifications][docs-util].
3. Some cool management commands that:

- Process all pending notifications.
- Create `UserInNotificationTarget` objects for the email target for all the current users in your database. Just in case you are adding this to an older project.

4. A straightforward and fairly easy way to for you to add support for addition notification types while tying into the existing functionality. No whining about it not being super easy! This is still a work in progress. :)

_Brought to you by the cool kids (er, kids that wanted to be cool) in the Center for Research Computing at Notre Dame._

# Requirements

- Python (3.5, 3.6, 3.7, 3.8)
- Django (3.1+)

We **highly recommend** and only officially support the latest patch release of
each Python and Django series.

# Installation

`pip install django-notification-system`

# Post-Install Setup (Optional)

If you would like to add support for addition types of notifications that don't exist in the package yet,
you'll need to add the following items to your Django settings. We will cover these items in more detail
in the [extending the system section of our docs][docs-ext]. So just a quick intro here.

**Django Settings Additions**

```python
# You will need to add email information as specified here: https://docs.djangoproject.com/en/3.1/topics/email/
# This can include:
EMAIL_HOST = ''
EMAIL_PORT = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
# and the EMAIL_USE_TLS and EMAIL_USE_SSL settings control whether a secure connection is used.

INSTALLED_APPS = [
    "django_notification_system", 
    ...]
# Add the following variables to your Django settings if
# you want to write modules to support additional notification
# types not included the library.

# A list of locations for the system to search for notification creators.
# You can just create the list and leave it empty if you want to just put this in place.
NOTIFICATION_SYSTEM_CREATORS = [
    '/path/to/creator_modules',
    '/another/path/to/creator_modules']

# A list of locations for the system to search for notification handlers.
# You can just create the list and leave it empty if you want to just put this in place.
NOTIFICATION_SYSTEM_HANDLERS = [
    '/path/to/handler_modules',
    '/another/path/to/handler_modules']

NOTIFICATION_SYSTEM_TARGETS = {
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
```

[pypi-version]: https://img.shields.io/pypi/v/django-notification-system.svg
[pypi]: https://pypi.org/project/django-notification-system/
[docs]: https://django-notification-system.readthedocs.io/en/latest/
[docs-ext]: https://django-notification-system.readthedocs.io/en/latest/extending.html
[docs-util]: https://django-notification-system.readthedocs.io/en/latest/utility_functions.html
