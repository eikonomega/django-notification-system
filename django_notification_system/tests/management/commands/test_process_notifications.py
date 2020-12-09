from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from exponent_server_sdk import PushResponse
from six import StringIO

from website.notifications.models import NotificationTarget, UserInNotificationTarget, Notification, NotificationOptOut
from website.api_v3.tests import factories
from website.notifications.utils.notification_handlers import handle_push_response
from ...mock_exponent_server_sdk import MockPushClient


@patch('website.notifications.utils.notification_handlers.PushClient', new=MockPushClient)
class TestCommand(TestCase):
    def setUp(self):
        # This will override environment variable to test production settings.
        self.env_prod = patch.dict("os.environ", {"ENVIRONMENT": "production"})
        # And QA settings
        self.env_qa = patch.dict("os.environ", {"ENVIRONMENT": "qa"})

        self.user_with_notifications = factories.UserFactory()

        self.dev_user = factories.UserFactory(is_superuser=True)

        self.target = factories.notifications.ExpoTargetFactory()

        self.target_email = factories.notifications.EmailTargetFactory()

        self.user_target = factories.notifications.Expo_UserTargetFactory(
            user=self.user_with_notifications
        )

        self.dev_user_target = factories.notifications.Expo_UserTargetFactory(
            user=self.dev_user,
        )

        self.user_target_email = UserInNotificationTarget.objects.get(
            user=self.user_with_notifications,
            target=self.target_email,
            active=True,
        )

        self.notification = Notification.objects.create(
            user_target=self.user_target,
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
            user_target=self.dev_user_target,
            status=Notification.SCHEDULED,
            title="Title",
            body="Whoops",
            scheduled_delivery=timezone.now() - timedelta(1),
        )

        self.notification_email = Notification.objects.create(
            user_target=self.user_target_email,
            status=Notification.SCHEDULED,
            title="Title",
            body="<p>Body of the message</p>",
            scheduled_delivery=timezone.now() - timedelta(1),
        )

        self.notification_not_to_push = Notification.objects.create(
            user_target=self.user_target,
            status=Notification.DELIVERED,
            title="Title2",
            body="Body of the message2",
            scheduled_delivery=timezone.now() - timedelta(2),
            attempted_delivery=timezone.now() - timedelta(1),
        )

        self.email_notification_not_to_push = Notification.objects.create(
            user_target=self.user_target_email,
            status=Notification.DELIVERED,
            title="Title2",
            body="<h1>Body of the message</h1>",
            scheduled_delivery=timezone.now() - timedelta(2),
            attempted_delivery=timezone.now() - timedelta(1),
        )

        self.notification_with_invalid_extra = Notification.objects.create(
            user_target=self.user_target,
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
        # Production settings
        with self.env_prod:
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
        # Production settings
        with self.env_prod:
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
        # Production settings
        with self.env_prod:
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

        self.user_with_notifications.notification_targets.all().all().delete()


        user_target_invalid_token = factories.notifications.Expo_UserTargetFactory(
            user=self.user_with_notifications,
            user_target_id="INVALID_TOKEN!!!!",
            user_target_friendly_name="Iphone 0",
        )

        notification_with_invalid_token = Notification.objects.create(
            user_target=user_target_invalid_token,
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

        # Production settings
        with self.env_prod:
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

    def test_qa_dev_team(self):
        """
        When this command is run on QA, we only want to send notifications to
        members of the development team.
        """
        # QA settings
        with self.env_qa:
            notification_to_push = Notification.objects.get(
                id=self.dev_notification.id
            )
            self.assertEqual(notification_to_push.status, Notification.SCHEDULED)
            self.assertIsNone(notification_to_push.attempted_delivery)

            notification_no_push = Notification.objects.get(id=self.notification.id)
            self.assertEqual(notification_no_push.status, Notification.SCHEDULED)
            self.assertIsNone(notification_no_push.attempted_delivery)

            call_command("process_notifications")

            notification_to_push = Notification.objects.get(
                id=self.dev_notification.id
            )
            self.assertEqual(notification_to_push.status, Notification.DELIVERED)
            self.assertIsNotNone(notification_to_push.attempted_delivery)

            notification_no_push = Notification.objects.get(id=self.notification.id)
            self.assertEqual(notification_no_push.status, Notification.SCHEDULED)
            self.assertIsNone(notification_no_push.attempted_delivery)

    def test_opt_out(self):
        with self.env_prod:
            with self.settings(DISABLE_EMAILS=False):
                user = factories.UserFactory()
                Notification.objects.create(
                    user_target=UserInNotificationTarget.objects.get(user=user),
                    status=Notification.SCHEDULED,
                    title="Notification to be recieved",
                    body="<p>Body of the message</p>",
                    scheduled_delivery="2018-10-24T12:42:13-04:00",
                )
                out = StringIO()
                call_command("process_notifications", stdout=out)
                self.assertIn(f"{user.username}", out.getvalue())

                Notification.objects.create(
                    user_target=UserInNotificationTarget.objects.get(user=user),
                    status=Notification.SCHEDULED,
                    title="Notification to Not be recieved 1",
                    body="<p>Body of the message</p>",
                    scheduled_delivery="2018-10-24T12:42:13-04:00",
                )

                NotificationOptOut.objects.create(user=user, has_opted_out=True)

                Notification.objects.create(
                    user_target=UserInNotificationTarget.objects.get(user=user),
                    status=Notification.SCHEDULED,
                    title="Notification to Not be recieved 2",
                    body="<p>Body of the message</p>",
                    scheduled_delivery="2018-10-24T12:42:13-04:00",
                )

                out = StringIO()
                call_command("process_notifications", stdout=out)
                self.assertNotIn(f"{user.username}", out.getvalue())

    def test_command__inactive_target(self):
        """
        Verify a Notification scheduled to be sent to an inactive device is marked as INACTIVE_DEVICE and ignored
        """
        # Production settings
        with self.env_prod:
            notification_to_push = Notification.objects.get(id=self.notification.id)

            notification_to_push.user_target = factories.notifications.Expo_UserTargetFactory(
                user=notification_to_push.user_target.user, active=False,
            )
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
                    user_target=notification_to_push.user_target,
                    title=notification_to_push.title,
                    body=notification_to_push.body,
                    extra=notification_to_push.extra,
                    scheduled_delivery=notification_to_push.scheduled_delivery,
                    related_object_uuid=notification_to_push.related_object_uuid,
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
