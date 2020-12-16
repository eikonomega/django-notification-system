from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from django.utils import timezone

from django_notification_system.exceptions import UserIsOptedOut
from django_notification_system.models.target_user_record import (
    TargetUserRecord,
)


def check_for_user_opt_out(user: User):
    """Determine if a user has an active opt-out.

    Args:
        user (User): The user to perform the check on.

    Raises:
        UserIsOptedOut: If the user has an active opt out.
    """
    if (
        hasattr(user, "notification_opt_out")
        and user.notification_opt_out.active
    ):
        raise UserIsOptedOut


def user_notification_targets(user: User, target_name: str):
    """Return all active user notifications targets for a given notification target.

    Args:
        user (User): The user to retrieve user targets for.
        target_name (str): The name of the target to retrieve user targets for.

    Returns:
        [UserInNotificationTarget]: A Django queryset of UserInNotificationTarget instances.
    """
    return TargetUserRecord.objects.filter(
        user=user,
        target__name=target_name,
        active=True,
    )


def check_and_update_retry_attempts(notification, minute_interval=None):
    """
    Check if the retry_attempt and max_retries are equal.
    If they are we want to change the status to DELIVERY_FAILURE.
    If not, we want to RETRY at a given minute interval.
    """
    if notification.max_retries != notification.retry_attempts:
        notification.retry_attempts += 1
        notification.save()
        # We have to go deeper...
        if notification.max_retries != notification.retry_attempts:
            notification.status = notification.RETRY
            if minute_interval is not None:
                notification.scheduled_delivery = (
                    timezone.now() + relativedelta(minutes=minute_interval)
                )
            else:
                notification.scheduled_delivery = (
                    timezone.now()
                    + relativedelta(minutes=notification.retry_time_interval)
                )
            notification.attempted_delivery = timezone.now()
            notification.save()

        else:
            notification.status = notification.DELIVERY_FAILURE
            notification.attempted_delivery = timezone.now()
            notification.save()
