import uuid

from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models

from website.abstract_models import CreatedModifiedAbstractModel
from .user_target import UserTarget


def get_default_data():
    return {}


class Notification(CreatedModifiedAbstractModel):

    """
    Definition of a Notification.

    Parameters
    ----------
    id : UUID
        The unique UUID of the record.
    user_target : UserTarget
        The UserTarget associated with notification
    title : str

    body : str
        The message to be sent.
    extra : dict
        a dictionary of extra data to be sent to Expo
        keys must be one of the following: ['data', 'sound', 'ttl', 'expiration', 'priority', 'badge', 'channel_id']
    status : CharField
        The status of Notification.  Choices determined by enum STATUS_CHOICES
    scheduled_delivery : DateTimeField
        Day and time Notification is to be sent.
    attempted_delivery : DateTImeField
        Day and time attempted to deliver Notification.
    related_object_uuid : UUID

    retry_time_interval : PositiveIntegerField
        The amount of time (in minutes) used to reschedule a notification
    retry_attempts : PositiveIntegerField
        The number of retries that have been attempted.
    max_retries : PositiveIntegerField
        The max number of allowed retries.

    Notes
    -----
    Notification is meant to strictly house the notifications that are to be
    sent.  There is to be a daemon that will then check this table and handle
    sending the notifications.

    """

    SCHEDULED = "SCHEDULED"
    DELIVERED = "DELIVERED"
    DELIVERY_FAILURE = "DELIVERY FAILURE"
    RETRY = "RETRY"
    INACTIVE_DEVICE = "INACTIVE DEVICE"

    STATUS_CHOICES = (
        (SCHEDULED, "Scheduled"),
        (DELIVERED, "Delivered"),
        (DELIVERY_FAILURE, "Delivery Failure"),
        (RETRY, "Retry"),
        (INACTIVE_DEVICE, "Inactive Device"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_target = models.ForeignKey(
        UserTarget, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=100)
    body = models.TextField()
    extra = JSONField(blank=True, null=True, default=get_default_data)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    scheduled_delivery = models.DateTimeField()
    attempted_delivery = models.DateTimeField(null=True, blank=True)
    related_object_uuid = models.CharField(
        max_length=100, null=True, blank=True, editable=False
    )
    retry_time_interval = models.PositiveIntegerField(default=0)
    retry_attempts = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)

    class Meta:
        db_table = "notifications_notification"
        verbose_name_plural = "Notifications"
        unique_together = ["user_target", "scheduled_delivery", "title", "extra"]

    def __str__(self):
        return "{} - {} - {}".format(
            self.user_target.user.username, self.status, self.scheduled_delivery
        )

    def clean(self):
        if self.attempted_delivery and self.status == "SCHEDULED":
            raise ValidationError(
                "Status cannot be 'SCHEDULED' if there is an Attempted Delivery."
            )

        elif not self.attempted_delivery and self.status != "SCHEDULED":
            raise ValidationError(
                "Attempted Delivery must be filled out if Status is {}".format(
                    self.status
                )
            )
        opted_out = (
            hasattr(self.user_target.user, "notification_opt_out")
            and self.user_target.user.notification_opt_out.has_opted_out
        )
        if opted_out:
            raise ValidationError("This user has opted out of Notifications.")
