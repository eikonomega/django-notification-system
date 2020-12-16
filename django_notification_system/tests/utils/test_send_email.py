
from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.utils import timezone


from django_notification_system.models import (
    Notification, NotificationTarget, TargetUserRecord)
from django_notification_system.notification_handlers.email import (
    send_notification)


class TestCreateEmailNotification(TestCase):
    def setUp(self):
        self.user_with_target = User.objects.create_user(
            username='sadboi@gmail.com',
            first_name='Sad',
            last_name='Boi',
            password='Ok.',
            email='sadboi@gmail.com')

        self.target_user_record = TargetUserRecord.objects.create(
            user=self.user_with_target,
            target=NotificationTarget.objects.get(name='Email'),
            target_user_id='sadboi@gmail.com',
            description='Sad Bois Email',
            active=True
        )

        self.notification = Notification.objects.create(
            target_user_record=self.target_user_record,
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

        response_message = send_notification(self.notification)

        self.assertEqual(response_message, 'Email Successfully Sent')
