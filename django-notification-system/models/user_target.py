import uuid

from django.conf import settings
from django.db import models
from django.db import transaction

from website.abstract_models import CreatedModifiedAbstractModel
from .target import Target


class UserTarget(CreatedModifiedAbstractModel):
    """
    Definition of a User Target

    A user target is a tie between a user and how they
    are identified in a given target.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_targets",
    )
    target = models.ForeignKey(Target, on_delete=models.PROTECT)
    user_target_id = models.CharField(max_length=200)
    user_target_friendly_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "notifications_user_target"
        verbose_name_plural = "User Targets"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "target", "user_target_id"],
                name="user target ids cannot be repeated",
            ),
            models.UniqueConstraint(
                condition=models.Q(active=True),
                fields=["user", "target", "user_target_friendly_name"],
                name="Only one active user target per friendly name",
            ),
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
            UserTarget.objects.filter(user=user, target=email_target,).update(
                active=False
            )

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
        return "{}: {}".format(self.user.username, self.user_target_friendly_name)
