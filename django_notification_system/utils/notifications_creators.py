from datetime import datetime
from uuid import UUID

from django.contrib.auth.models import User
from django.template.loader import get_template
from django.utils import timezone

from ..models import Notification, UserTarget


def create_expo_notifications(
    user: User,
    title: str,
    body: str,
    scheduled_delivery: datetime = None,
    extra: dict = None,
    related_object_uuid: UUID = None,
    retry_time_interval: int = 1,
    max_retries: int = 3,
    quiet=True,
) -> None:
    """
    This function creates a notification to be sent

    Parameters
    ----------
    user
        a user
    title
        a title
    body
        the body of the notification
    extra : dict
        a dict of extra parameters to be sent to expo
    scheduled_delivery
        defaults to now
    related_object_uuid
        e.g. workflow uuid
    retry_time_interval
        defaults to 1 second
    max_retries
        defaults to 3
    quiet
        whether or not the function should raise an exception if no notification is sent
    Returns
    -------
    True, if any notifications were scheduled
    False, if no notifications were scheduled
    """

    opted_out = (
        hasattr(user, "notification_opt_out")
        and user.notification_opt_out.has_opted_out
    )

    if opted_out:
        if quiet:
            return
        else:
            raise UserIsOptedOut()

    if scheduled_delivery is None:
        scheduled_delivery = timezone.now()

    user_targets = UserTarget.objects.filter(
        user=user,
        target__class_name="Expo",
        active=True,
    )

    if not user_targets.count():
        if quiet:
            return
        else:
            raise UserHasNoTargets()

    notification_sent = False
    for user_target in user_targets:
        # JSONField casts None to {}, so we have to check if the server value = {}
        if extra is None:
            extra = {}  # I hate casting so much
        _, created = Notification.objects.get_or_create(
            user_target=user_target,
            title=title,
            scheduled_delivery=scheduled_delivery,
            extra=extra,
            defaults={
                "body": body,
                "status": "SCHEDULED",
                "related_object_uuid": related_object_uuid,
                "retry_time_interval": retry_time_interval,
                "max_retries": max_retries,
            },
        )
        notification_sent = notification_sent or created
    if not notification_sent:
        if quiet:
            return
        else:
            raise NotificationNotSent()
