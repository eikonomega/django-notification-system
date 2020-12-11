
from unittest.mock import patch
from smtplib import SMTPException

from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.utils import timezone


from django_notification_system.models import (
    Notification, NotificationTarget, TargetUserRecord)

from django_notification_system.notification_handlers.email import send_notification


class TestSMTPExceptionEmailNotification(TestCase):
    def setUp(self):
        self.user_with_target = User.objects.create_user(
            username='sadboi@gmail.com',
            first_name='Sad',
            last_name='Boi',
            password='Ok.',
            email='sadboi@gmail.com')

        self.target, created = NotificationTarget.objects.get_or_create(
            name='Email',
            notification_module_name='email'
        )

        self.user_target = TargetUserRecord.objects.create(
            user=self.user_with_target,
            target=self.target,
            target_user_id='sadboi@gmail.com',
            description="Sad Boi's Email",
            active=True
            )

        self.notification = Notification.objects.create(
            target_user_record=self.user_target,
            title="Hi.",
            body="<b>It me. Is it me?</b>",
            status='SCHEDULED',
            scheduled_delivery=timezone.now(),
            max_retries=2)

    def test_smtp_exception(self):
        """
        Test that an smtp_exception is correctly handled.
        """
        with patch('django.core.mail.send_mail') as fake_send:
            fake_send.side_effect = SMTPException("No server")

            # Assert exception is correctly handled
            response_message = send_notification(
                self.notification)

            self.assertEqual(response_message,
                             'Email could not be sent: No server')
            # Assert DELIVERY_FAILURE after max_retries hit
            send_notification(self.notification)
            self.assertEqual(self.notification.status, 'DELIVERY FAILURE')
