from datetime import datetime
from django_notification_system.utils import (
    check_for_user_opt_out,
    user_notification_targets,
)

from django.contrib.auth.models import User
from django.utils import timezone

from ..models import Notification
from ..exceptions import (
    NotificationsNotCreated,
    UserHasNoTargetRecords,
    UserIsOptedOut,
)


def create_notification(
    user: User,
    title: str,
    body: str,
    scheduled_delivery: datetime = None,
    retry_time_interval: int = 1440,
    max_retries: int = 3,
    quiet=False,
    extra: dict = None,
) -> None:
    """
    This function will generate a Twilio SMS notification.

    Args:
        user (User): The user to whom the push notification will be sent.
        title (str): The title for the push notification.
        body (str, optional): The body of the sms notification.
        scheduled_delivery (datetime, optional): Defaults to immediately.
        retry_time_interval (int, optional): Delay between send attempts. Defaults to 60 seconds.
        max_retries (int, optional): Maximum number of retry attempts for delivery. Defaults to 3.
        quiet (bool, optional): Suppress exceptions from being raised. Defaults to False.
        extra (dict, optional): Defaults to None.

    Raises:
        UserIsOptedOut: When the user has an active opt-out.
        UserHasNoTargetRecords: When the user has no eligible targets for this notification type.
        NotificationsNotCreated: When the notifications could not be created.
    """
    try:
        check_for_user_opt_out(user=user)
    except UserIsOptedOut:
        if quiet:
            return
        else:
            raise UserIsOptedOut()

    target_user_records = user_notification_targets(user=user, target_name="Twilio")

    if not target_user_records:
        if quiet:
            return
        else:
            raise UserHasNoTargetRecords()

    if scheduled_delivery is None:
        scheduled_delivery = timezone.now()

    notifications_created = []
    for target_user_record in target_user_records:
        # JSONField casts None to {}, so we have to check if the server value = {}
        if extra is None:
            extra = {}  # I hate casting so much
        notification, created = Notification.objects.get_or_create(
            target_user_record=target_user_record,
            title=title,
            scheduled_delivery=scheduled_delivery,
            extra=extra,
            defaults={
                "body": body,
                "status": 'SCHEDULED',
                "retry_time_interval": retry_time_interval,
                "max_retries": max_retries
            }
        )

        if created:
            notifications_created.append(notification)

    if not notifications_created:
        if quiet:
            return
        else:
            raise NotificationsNotCreated()
