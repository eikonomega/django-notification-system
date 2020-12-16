from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from exponent_server_sdk import PushResponse
from six import StringIO

from django_notification_system.models import (
    NotificationTarget, TargetUserRecord, Notification, NotificationOptOut)
from django_notification_system.notification_handlers.expo import handle_push_response
from ...mock_exponent_server_sdk import MockPushClient


@patch('django_notification_system.notification_handlers.expo.PushClient', new=MockPushClient)
class TestCommand(TestCase):
    def setUp(self):
        self.user_with_notifications = User.objects.create_user(
            username="Eggless",
            email="eggless@gmail.com",
            first_name="Egg",
            last_name="Less",
            password="ImpressivePassword")

        self.dev_user = User.objects.create_user(
            username="Danglesauce",
            email="danglesauce@gmail.com",
            first_name="Dangle",
            last_name="Sauce",
            password="ImpressivePassword")

        self.user_target = TargetUserRecord.objects.create(
            user=self.user_with_notifications,
            target=NotificationTarget.objects.get(name='Expo'),
            target_user_id='ExponentPushToken[ByAAmjPd96SUb1Is5eUzXX]',
            description="It's Expo",
            active=True
        )

        self.dev_user_target = TargetUserRecord.objects.create(
            user=self.dev_user,
            target=NotificationTarget.objects.get(name="Expo"),
            target_user_id='ExponentPushToken[ByAAmjPd96SUb1Is5eUzXX]',
            description='Dangle Expo',
            active=True
        )

        self.user_target_email = TargetUserRecord.objects.create(
            user=self.user_with_notifications,
            target=NotificationTarget.objects.get(name='Email'),
            target_user_id=self.user_with_notifications.email,
            description='Its email',
            active=True,
        )

        self.user_target_twilio = TargetUserRecord.objects.create(
            user=self.user_with_notifications,
            target=NotificationTarget.objects.get(name='Twilio'),
            target_user_id='6766676677',
            description='Test Phone #',
            active=True
        )

        self.notification = Notification.objects.create(
            target_user_record=self.user_target,
            status=Notification.SCHEDULED,
            title="Title",
            body="Body of the message",
            extra={
                "sound": "default",
                "data": {"Junk": "Junk"},
                "priority": "high",
                "ttl": "3",
                "expiration": "1486080000",
                "badge": "3",
            },
            scheduled_delivery="2018-10-24T12:42:13-04:00",
        )

        self.dev_notification = Notification.objects.create(
            target_user_record=self.dev_user_target,
            status=Notification.SCHEDULED,
            title="Title",
            body="Whoops",
            scheduled_delivery=timezone.now() - timedelta(1),
        )

        self.notification_email = Notification.objects.create(
            target_user_record=self.user_target_email,
            status=Notification.SCHEDULED,
            title="Title",
            body="<p>Body of the message</p>",
            scheduled_delivery=timezone.now() - timedelta(1),
        )

        self.notification_twilio = Notification.objects.create(
            target_user_record=self.user_target_twilio,
            status=Notification.SCHEDULED,
            title='Test SMS',
            body="Whoops",
            scheduled_delivery=timezone.now() - timedelta(1),
        )

        self.notification_not_to_push = Notification.objects.create(
            target_user_record=self.user_target,
            status=Notification.DELIVERED,
            title="Title2",
            body="Body of the message2",
            scheduled_delivery=timezone.now() - timedelta(2),
            attempted_delivery=timezone.now() - timedelta(1),
        )

        self.email_notification_not_to_push = Notification.objects.create(
            target_user_record=self.user_target_email,
            status=Notification.DELIVERED,
            title="Title2",
            body="<h1>Body of the message</h1>",
            scheduled_delivery=timezone.now() - timedelta(2),
            attempted_delivery=timezone.now() - timedelta(1),
        )

        self.notification_with_invalid_extra = Notification.objects.create(
            target_user_record=self.user_target,
            status=Notification.SCHEDULED,
            title="Title3",
            body="Body of the message3",
            extra={"sound": "BAD_SOUND!"},
            scheduled_delivery=timezone.now() - timedelta(1),
        )

    def test_command__successful_push(self):
        """
        Verify a Notification that is SCHEDULED, has a scheduled_delivery that is earlier than
        the current datetime, and has valid 'extra' data gets pushed and updated correctly.
        """
        notification_to_push = Notification.objects.get(id=self.notification.id)
        self.assertEqual(notification_to_push.status, Notification.SCHEDULED)
        self.assertIsNone(notification_to_push.attempted_delivery)

        email_notification_to_push = Notification.objects.get(
            id=self.notification.id
        )
        self.assertEqual(email_notification_to_push.status, Notification.SCHEDULED)
        self.assertIsNone(email_notification_to_push.attempted_delivery)

        out = StringIO()
        call_command("process_notifications", stdout=out)

        notification_to_push = Notification.objects.get(id=self.notification.id)
        self.assertEqual(notification_to_push.status, Notification.DELIVERED)
        self.assertIsNotNone(notification_to_push.attempted_delivery)

        email_notification_to_push = Notification.objects.get(
            id=self.notification.id
        )
        self.assertEqual(email_notification_to_push.status, Notification.DELIVERED)
        self.assertIsNotNone(email_notification_to_push.attempted_delivery)

    def test_command__no_push(self):
        """
        Verify a Notification that is already DELIVERED doesn't get pushed or updated
        """
        notification_not_to_push = Notification.objects.get(
            id=self.notification_not_to_push.id
        )
        notification_not_to_push_attempted_delivery = notification_not_to_push.attempted_delivery
        self.assertEqual(notification_not_to_push.status, Notification.DELIVERED)
        self.assertEqual(
            notification_not_to_push.attempted_delivery, notification_not_to_push_attempted_delivery
        )

        email_notification_not_to_push = Notification.objects.get(
            id=self.email_notification_not_to_push.id
        )
        email_notification_not_to_push_attempted_delivery = email_notification_not_to_push.attempted_delivery
        self.assertEqual(
            email_notification_not_to_push.status, Notification.DELIVERED
        )
        self.assertEqual(
            email_notification_not_to_push.attempted_delivery, email_notification_not_to_push_attempted_delivery
        )

        out = StringIO()
        call_command("process_notifications", stdout=out)

        notification_not_to_push = Notification.objects.get(
            id=self.notification_not_to_push.id
        )
        self.assertEqual(notification_not_to_push.status, Notification.DELIVERED)
        self.assertEqual(
            notification_not_to_push.attempted_delivery, notification_not_to_push_attempted_delivery
        )

        email_notification_not_to_push = Notification.objects.get(
            id=self.email_notification_not_to_push.id
        )
        self.assertEqual(
            email_notification_not_to_push.status, Notification.DELIVERED
        )
        self.assertEqual(
            email_notification_not_to_push.attempted_delivery, email_notification_not_to_push_attempted_delivery
        )

    def test_command__failed_push(self):
        """
        Verify a Notification that is SCHEDULED, has a scheduled_delivery that is earlier than
        the current datetime, but has invalid 'extra' data doesn't get pushed and gets updated
        correctly.
        """
        notification_with_invalid_extra = Notification.objects.get(
            id=self.notification_with_invalid_extra.id
        )
        self.assertEqual(
            notification_with_invalid_extra.status, Notification.SCHEDULED
        )
        self.assertIsNone(notification_with_invalid_extra.attempted_delivery)

        out = StringIO()
        call_command("process_notifications", stdout=out)

        notification_with_invalid_extra = Notification.objects.get(
            id=self.notification_with_invalid_extra.id
        )
        self.assertEqual(notification_with_invalid_extra.status, Notification.RETRY)
        self.assertIsNotNone(notification_with_invalid_extra.attempted_delivery)

    def test_command__invalid_token(self):
        """
        Verify a Notification that is SCHEDULED, has a scheduled_delivery that is earlier than
        the current datetime, and has valid 'extra' data, but has an invalid token
        doesn't get pushed and updated correctly.
        """
        self.user_with_notifications.notification_target_user_records.all().all().delete()

        user_target_invalid_token = TargetUserRecord.objects.create(
            user=self.user_with_notifications,
            target=NotificationTarget.objects.get(name='Expo'),
            target_user_id="INVALID_TOKEN!!!!",
            description="Iphone 0",
        )

        notification_with_invalid_token = Notification.objects.create(
            target_user_record=user_target_invalid_token,
            status=Notification.SCHEDULED,
            title="Title4",
            body="Body of the message4",
            extra={
                "sound": "default",
                "data": {"Junk": "Junk"},
                "priority": "high",
                "ttl": "3",
                "expiration": "1486080000",
                "badge": "3",
            },
            scheduled_delivery="2018-10-24T12:42:13-04:00",
        )

        self.assertEqual(
            notification_with_invalid_token.status, Notification.SCHEDULED
        )
        self.assertIsNone(notification_with_invalid_token.attempted_delivery)

        out = StringIO()
        call_command("process_notifications", stdout=out)

        notification_with_invalid_token = Notification.objects.get(
            id=notification_with_invalid_token.id
        )
        self.assertEqual(notification_with_invalid_token.status, Notification.RETRY)
        self.assertIsNotNone(notification_with_invalid_token.attempted_delivery)

    def test_opt_out(self):
        user = User.objects.create_user(
            username="charlie",
            email="cbuckets@gmail.com",
            first_name="Charlie",
            last_name="Buckets",
            password="ImpressivePassword"
        )
        target_user_record = TargetUserRecord.objects.create(
            user=user,
            target=NotificationTarget.objects.get(name='Email'),
            target_user_id=user.email,
            description="Charlie email",
            active=True
        )
        Notification.objects.create(
            target_user_record=target_user_record,
            status=Notification.SCHEDULED,
            title="Notification to be recieved",
            body="<p>Body of the message</p>",
            scheduled_delivery="2018-10-24T12:42:13-04:00",
        )
        out = StringIO()
        call_command("process_notifications", stdout=out)

        Notification.objects.create(
            target_user_record=target_user_record,
            status=Notification.SCHEDULED,
            title="Notification to Not be recieved 1",
            body="<p>Body of the message</p>",
            scheduled_delivery="2018-10-24T12:42:13-04:00",
        )

        Notification.objects.create(
            target_user_record=target_user_record,
            status=Notification.SCHEDULED,
            title="Notification to Not be recieved 2",
            body="<p>Body of the message</p>",
            scheduled_delivery="2018-10-24T12:42:13-04:00",
        )

        NotificationOptOut.objects.create(user=user, active=True)

        call_command("process_notifications", stdout=out)

        notif_not_sent_1 = Notification.objects.get(
            target_user_record=target_user_record,
            title="Notification to Not be recieved 1")
        notif_not_sent_2 = Notification.objects.get(
            target_user_record=target_user_record,
            title="Notification to Not be recieved 2")

        self.assertEqual(notif_not_sent_1.status, "OPTED OUT")
        self.assertEqual(notif_not_sent_2.status, "OPTED OUT")

    def test_command__inactive_target(self):
        """
        Verify a Notification scheduled to be sent to an inactive device is marked as INACTIVE_DEVICE and ignored
        """
        notification_to_push = Notification.objects.get(id=self.notification.id)
        target_user_record = TargetUserRecord.objects.get(
            user=notification_to_push.target_user_record.user, target__name='Expo')
        target_user_record.active = False
        target_user_record.save()
        notification_to_push.user_target = target_user_record
        notification_to_push.save()

        self.assertEqual(notification_to_push.status, Notification.SCHEDULED)
        self.assertIsNone(notification_to_push.attempted_delivery)

        out = StringIO()
        call_command("process_notifications", stdout=out)

        notification_to_push = Notification.objects.get(id=self.notification.id)
        self.assertEqual(notification_to_push.status, Notification.INACTIVE_DEVICE)
        self.assertIsNone(notification_to_push.attempted_delivery)

        self.assertEqual(
            Notification.objects.filter(
                target_user_record=notification_to_push.target_user_record,
                title=notification_to_push.title,
                body=notification_to_push.body,
                extra=notification_to_push.extra,
                scheduled_delivery=notification_to_push.scheduled_delivery
            ).count(),
            1,
        )

    def test_deactivates_on_device_not_registered(self):
        """
        Test that a user target is deactivated
        when Expo/Firebase Cloud Messaging returns
        a device not registered error.
        Returns
        -------

        """
        self.assertEqual(self.dev_user_target.active, True)
        response = PushResponse(
            push_message="",
            status=PushResponse.ERROR_STATUS,
            message='"adsf" is not a registered push notification recipient',
            details={'error': PushResponse.ERROR_DEVICE_NOT_REGISTERED}
        )
        handle_push_response(self.dev_notification, response=response)
        self.dev_user_target.refresh_from_db()
        self.assertEqual(self.dev_user_target.active, False)
