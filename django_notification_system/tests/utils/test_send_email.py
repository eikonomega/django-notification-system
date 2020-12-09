
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.utils import timezone


from website.notifications.models import (
    Notification, NotificationTarget, UserInNotificationTarget)
from website.notifications.utils.notification_handlers import (
    send_email)


class TestCreateEmailNotification(TestCase):
    def setUp(self):
        self.user_with_target = User.objects.create_user(
            username='sadboi@gmail.com',
            first_name='Sad',
            last_name='Boi',
            password='Ok.',
            email='sadboi@gmail.com')

        self.user_with_target.save()

        self.notification = Notification.objects.create(
            user_target=UserInNotificationTarget.objects.get(user=self.user_with_target),
            title="Hi.",
            body="<b>It me. Is it me?</b>",
            status='SCHEDULED',
            scheduled_delivery=timezone.now())

    def test_send_email(self):
        """
        Test proper functionality of send_email function.
        """
        pre_function_notification = Notification.objects.all()
        self.assertEqual(pre_function_notification[0].status,
                         'SCHEDULED')

        response_message = send_email(self.notification)

        self.assertEqual(response_message, 'Email Successfully Sent')
