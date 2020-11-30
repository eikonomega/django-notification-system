
from unittest.mock import patch
from smtplib import SMTPException

from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.utils import timezone


from website.notifications.models import (
    Notification, Target, UserTarget)

from website.notifications.utils.notification_handlers import send_email


class TestSMTPExceptionEmailNotification(TestCase):
    def setUp(self):
        self.user_with_target = User.objects.create_user(
            username='sadboi@gmail.com',
            first_name='Sad',
            last_name='Boi',
            password='Ok.',
            email='sadboi@gmail.com')

        self.user_with_target.save()

        self.notification = Notification.objects.create(
            user_target=UserTarget.objects.get(user=self.user_with_target),
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
            response_message = send_email(
                self.notification)

            self.assertEqual(response_message,
                             'Email could not be sent: No server')
            # Assert DELIVERY_FAILURE after max_retries hit
            send_email(self.notification)
            self.assertEqual(self.notification.status, 'DELIVERY FAILURE')
