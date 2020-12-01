from datetime import datetime

from django.contrib.auth.models import User
from django.template.loader import get_template

from ..models import Notification, UserTarget
from ..exceptions import (
    NotificationNotSent,
    UserHasNoTargets,
    UserIsOptedOut,
)


def create_notification(
    user: User,
    title: str,
    template_name: str,
    scheduled_delivery: datetime = None,
    retry_time_interval: int = 1440,
    max_retries: int = 3,
    quiet=False,
    **context_variables,
) -> None:
    """
    This function will generate an email body based on an
    email template within the code base.

    Args:
        user (User): The user to whom the notification will be sent.
        title (str): The title for the notification.
        template_name (str): The name of the email template to use. This is will be searched for in the directories specified by SETTING_INFO_GOES_HERE.
        scheduled_delivery (datetime, optional): When to delivery the notification. Defaults to immediately.
        retry_time_interval (int, optional): When to retry sending the notification if a delivery failure occurs. Defaults to 1440 seconds.
        max_retries (int, optional): [description]. Maximum number of retry attempts. Defaults to 3.
        quiet (bool, optional): Suppress exceptions from being raised. Defaults to False.
        **context_variables: context variables for django template

    Raises:
        UserIsOptedOut: [description]
        UserHasNoTargets: [description]
        NotificationNotSent: [description]
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

    template = get_template(template_name)
    html_code = template.render(context_variables)

    user_targets = UserTarget.objects.filter(
        user=user,
        target__notification_creator_module="email",
        active=True,
    )

    if not user_targets.count():
        if quiet:
            return
        else:
            raise UserHasNoTargets()
    notification_sent = False
    for user_target in user_targets:
        _, created = Notification.objects.get_or_create(
            user_target=user_target,
            title=title,
            scheduled_delivery=scheduled_delivery,
            defaults={
                "body": html_code,
                "status": "SCHEDULED",
                "related_object_uuid": related_object_uuid,
                "retry_time_interval": retry_time_interval,
                "max_retries": max_retries,
            },
        )
        if created:
            notification_sent = True
    if not notification_sent:
        if quiet:
            return
        else:
            raise NotificationNotSent()