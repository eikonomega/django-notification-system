import uuid

from django.db import models

from .abstract import CreatedModifiedAbstractModel


class NotificationTarget(CreatedModifiedAbstractModel):
    """
    Definition of a Notification Target.

    A target represents something that can receive a
    notication from our system.

    Attributes
    ----------
    id : UUID
        The unique UUID of the record.
    name : CharField
        The human friendly name for the target.
    notification_module_name : str
        The name of the module in the notification_creators directory which
        will be used to create notifications for this target.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=15, unique=True)
    notification_module_name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "notification_system_target"
        verbose_name_plural = "Notification Targets"
