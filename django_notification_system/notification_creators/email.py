from datetime import datetime
from django_notification_system.utils import (
    check_for_user_opt_out,
    user_notification_targets,
)

from django.contrib.auth.models import User
from django.template.loader import get_template
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
    body: str = "",
    scheduled_delivery: datetime = None,
    retry_time_interval: int = 1440,
    max_retries: int = 3,
    quiet=False,
    extra: dict = None,
) -> None:
    """
    This function will generate an email notification.

    Args:
        user (User): The user to whom the notification will be sent.
        title (str): The title for the notification.
        body (str, optional): Body of the email. Defaults to a blank string if not given.
            Additionally, if this parameter is not specific AND "template_name" is present
            in `extra`, an attempt will be made to generate the body from that template.
        scheduled_delivery (datetime, optional): When to delivery the notification. Defaults to immediately.
        retry_time_interval (int, optional): When to retry sending the notification if a delivery failure occurs. Defaults to 1440 seconds.
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        quiet (bool, optional): Suppress exceptions from being raised. Defaults to False.
        extra (dict, optional): User specified additional data that will be used to
            populate an HTML template if "template_name" is present inside.

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

    target_user_records = user_notification_targets(user=user, target_name="Email")

    if not target_user_records:
        if quiet:
            return
        else:
            raise UserHasNoTargetRecords()

    if scheduled_delivery is None:
        scheduled_delivery = timezone.now()

    # Determine the body of the email. Preference is
    if body:
        email_body = body
    elif "template_name" in extra:
        # TODO: Look into how this function works and if we can just instruct people to include email templates in the TEMPLATE_DIRS setting.
        template = get_template(extra["template_name"])
        email_body = template.render(**extra)
    else:
        raise ValueError(
            "You must either specify a `body` value or include 'template_name' in `extra` to create an email notification."
        )

    notifications_created = []
    for target_user_record in target_user_records:
        notification, created = Notification.objects.get_or_create(
            target_user_record=target_user_record,
            title=title,
            scheduled_delivery=scheduled_delivery,
            defaults={
                "body": email_body,
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
