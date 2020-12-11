import uuid

from django.conf import settings
from django.db import models
from django.db import transaction

from .abstract import CreatedModifiedAbstractModel
from .target import NotificationTarget


class TargetUserRecord(CreatedModifiedAbstractModel):
    """
    Definition of a TargetUserRecord.

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
        related_name="notification_target_user_records",
    )
    target = models.ForeignKey(NotificationTarget, on_delete=models.PROTECT)
    target_user_id = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_system_target_user_record"
        verbose_name_plural = "User In Notification Targets"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "target", "target_user_id"],
                name="user target ids cannot be repeated",
            )
        ]

    def __str__(self):
        return "{}: {}".format(self.user.username, self.description)
