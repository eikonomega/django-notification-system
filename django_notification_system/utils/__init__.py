from django.contrib.auth.models import User

from django_notification_system.exceptions import UserIsOptedOut
from django_notification_system.models.user_target import UserTarget


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
        [UserTarget]: A Django queryset of UserTarget instances.
    """
    return UserTarget.objects.filter(
        user=user,
        target__name=target_name,
        active=True,
    )