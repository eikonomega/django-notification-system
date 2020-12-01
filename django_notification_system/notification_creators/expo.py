from datetime import datetime
from django_notification_system.exceptions import (
    NotificationsNotCreated,
    UserHasNoTargets,
    UserIsOptedOut,
)
from django_notification_system.utils import (
    check_for_user_opt_out,
    user_notification_targets,
)

from django.contrib.auth.models import User
from django.utils import timezone

from ..models import Notification

# TODO: Document what keys Expo supports for the `extra` argument.
def create_notification(
    user: User,
    title: str,
    body: str,
    scheduled_delivery: datetime = None,
    retry_time_interval: int = 60,
    max_retries: int = 3,
    quiet=False,
    extra: dict = None,
) -> None:
    """
    This function will generate an Expo push notification. Expo is a service
    that is commonly used in React Native mobile development.

    Args:
        user (User): The user to whom the push notification will be sent.
        title (str): The title for the push notification.
        body (str): [description]. The body of the push notification.
        scheduled_delivery (datetime, optional): [description]. Defaults to immediately.
        retry_time_interval (int, optional): Delay between send attempts. Defaults to 60 seconds.
        max_retries (int, optional): Maximum number of retry attempts for delivery. Defaults to 3.
        quiet (bool, optional): Suppress exceptions from being raised. Defaults to False.
        extra (dict, optional): [description]. Defaults to None.

    Raises:
        UserIsOptedOut: [description]
        UserHasNoTargets: [description]
        NotificationNotSent: [description]
    """

    try:
        check_for_user_opt_out(user=user)
    except UserIsOptedOut:
        if quiet:
            return
        else:
            raise UserIsOptedOut()

    user_targets = user_notification_targets(user=user, target_name="Expo")

    # TODO: Does this need to have .count()?
    if not user_targets.count():
        if quiet:
            return
        else:
            raise UserHasNoTargets()

    if scheduled_delivery is None:
        scheduled_delivery = timezone.now()

    notifications_created = []
    for user_target in user_targets:
        # JSONField casts None to {}, so we have to check if the server value = {}
        if extra is None:
            extra = {}  # I hate casting so much
        notification, created = Notification.objects.get_or_create(
            user_target=user_target,
            title=title,
            scheduled_delivery=scheduled_delivery,
            extra=extra,
            defaults={
                "body": body,
                "status": "SCHEDULED",
                "retry_time_interval": retry_time_interval,
                "max_retries": max_retries,
            },
        )

        if created:
            notifications_created.append(notification)

    if not notifications_created:
        if quiet:
            return
        else:
            raise NotificationsNotCreated()
