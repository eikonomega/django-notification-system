import uuid

from django.conf import settings
from django.db import models
from django.db import transaction

from .abstract import CreatedModifiedAbstractModel
from .target import Target


class UserTarget(CreatedModifiedAbstractModel):
    """
    Definition of a User Target

    Each user will have a unique ID for each notification target,
    which is how we identify the individual who will receive the
    notification.

    For example, for an email target, we need to store the
    user's email address.

    Attributes
    ----------
    id : UUID
        The unique UUID of the record.
    user : Django User / Custom User Instance
        The User/Custom User instance associated with this record.
    target: Foreign Key
        The associated target instance.
    target_user_id : str
        The ID used in the target to uniquely identify the user.
    description : str
        A human friendly note about the user target.
    active : boolean
        Indicator of whether user target is active or not. For example,
        we have an outdated email record for a user.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_targets",
    )
    target = models.ForeignKey(Target, on_delete=models.PROTECT)
    target_user_id = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_system_user_target"
        verbose_name_plural = "User Targets"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "target", "target_user_id"],
                name="user target ids cannot be repeated",
            )
        ]

    @staticmethod
    def reset_email_target(user):
        """
        sets the user's email target to their current email
        Parameters
        ----------
        user: a user
        """
        email_target, created = Target.objects.get_or_create(
            name="Email", class_name="Email"
        )

        with transaction.atomic():
            # using atomic so user always has a valid email

            # Mark all their previous emails as inactive
            UserTarget.objects.filter(
                user=user,
                target=email_target,
            ).update(active=False)

            UserTarget.objects.update_or_create(
                user=user,
                target=email_target,
                user_target_id=user.email,
                defaults={
                    "active": True,
                    "user_target_friendly_name": f"{user.first_name} {user.last_name}'s Email",
                },
            )
        return

    def __str__(self):
        return "{}: {}".format(
            self.user.username, self.user_target_friendly_name
        )
