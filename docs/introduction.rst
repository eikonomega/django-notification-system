Perhaps you've got a Django application that you'd like to send notifications from? 

Well, we certainly have our share of them. And guess what? We're tired of writing code to create and send various
types of messages over and over again! 

So, we've created this package to simplify things
a bit for future projects. Hopefully, it will help you too.

**Here's the stuff you get:**

1. A few Django :doc:`models<../models>` that are pretty important:

  * `Notification`: A single notification. Flexible enough to handle many different types of notifications.
  * `NotificationTarget`: A target for notifications. Email, SMS, etc.
  * `TargetUserRecord`: Info about the user in a given target (Ex. Your "address" in the "email" target).
  * `NotificationOptOut`: Single location to keep track of user opt outs. You don't want the spam police after you.

2. Built in support for :doc:`email, Twilio SMS, and Expo push notifications. <../utility_functions>`.
3. Some cool management commands that:

  * Process all pending notifications.
  * Create `UserInNotificationTarget` objects for the email target for all the current users in your database. Just in case you are adding this to an older project.

4. A straightforward and fairly easy way to for you to add support for addition notification types while tying into the existing functionality. No whining about it not being super easy! This is still a work in progress. :) 


*Brought to you by the cool kids (er, kids that wanted to be cool) in the Center for Research Computing at Notre Dame.*