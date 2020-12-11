Installation
=================================

Requirements
----------------------------------
* Python 3. Yes, we have completely ignored Python 2. Sad face.
* Django 2+
* A computer... preferrably plugged in.

Excuse me sir, may I have another?
----------------------------------
Only the nerdiest of nerds put Dickens puns in their installation docs.

`pip install django-notification-system`

Post-Install Setup (Optional)
----------------------------------
If you would like to add support for addition types of notifications that don't exist in the package yet, 
you'll need to add the following items to your Django settings. We will cover these items in more detail
in the :doc:`extending the system <../extending>`. So just a quick intro here.

**Django Settings Additions**
        .. code-block:: python

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
                
                # Twilio Required settings, if you're not planning on using Twilio these can be set
                # to empty strings
                TWILIO_ACCOUNT_SID = 'FAKE_SID_FOR_DEMO_PURPOSES'
                TWILIO_AUTH_TOKEN = 'FAKE_TOKEN_FOR_DEMO_PURPOSES'
                TWILIO_SENDER = '+15555555555'
                
