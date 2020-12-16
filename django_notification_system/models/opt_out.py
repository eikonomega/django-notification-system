import uuid

from django.conf import settings
from django.db import models

from .abstract import CreatedModifiedAbstractModel
from .notification import Notification


class NotificationOptOut(CreatedModifiedAbstractModel):
    """
    Definition of a User Opt-Out Model.

    Users who have opted-out of communications will have an instance of this model.

    Attributes
    ----------
    id : UUID
        The unique UUID of the record.
    user : Django User / Custom User Instance
        The User/Custom User instance associated with this record.
    active : boolean
        Indicator for whether the opt out is active or not.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_opt_out",
    )
    active = models.BooleanField(default=False)

    class Meta:
        db_table = "notification_system_opt_out"
        verbose_name_plural = "Notification Opt Outs"

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        """
        When an instance of this model is saved, if the opt out is active
        change the status of notifications with a current status of
        SCHEDULED or RETRY to OPTED_OUT.
        """
        if self.active:
            Notification.objects.filter(
                status__in=[Notification.SCHEDULED, Notification.RETRY],
                target_user_record__user=self.user,
            ).update(status=Notification.OPTED_OUT)
        super(NotificationOptOut, self).save(*args, **kwargs)
