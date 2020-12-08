import uuid

from django.core.exceptions import ValidationError
from django.db import models

from .abstract import CreatedModifiedAbstractModel
from .user_target import UserTarget


class Notification(CreatedModifiedAbstractModel):
    """
    Definition of a Notification.

    Attributes
    ----------
    id : UUID
        The unique UUID of the record.
    user_target : UserTarget
        The UserTarget associated with notification
    title : str
        The title for the notification. Exact representation depends on the target.
        For example, for an email notification this will be used as the subject of the email.
    body : str
        The main message of the notification to be sent.
    extra : dict
        A dictionary of extra data to be sent to the notification processor. Valid keys
        are determined by each processor.
    status : CharField
        The status of Notification. Options are: 'SCHEDULED', 'DELIVERED', 'DELIVERY_FAILURE', 'RETRY', 'INACTIVE_DEVICE'
    scheduled_delivery : DateTimeField
        Day and time Notification is to be sent.
    attempted_delivery : DateTImeField
        Day and time attempted to deliver Notification.
    retry_time_interval : PositiveIntegerField
        If a notification fails, this is the amount of time to wait until retrying to send it.
    retry_attempts : PositiveIntegerField
        The number of retries that have been attempted.
    max_retries : PositiveIntegerField
        The max number of allowed retries.
    """

    DELIVERED = "DELIVERED"
    DELIVERY_FAILURE = "DELIVERY FAILURE"
    INACTIVE_DEVICE = "INACTIVE DEVICE"
    OPTED_OUT = "OPTED OUT"
    RETRY = "RETRY"
    SCHEDULED = "SCHEDULED"

    STATUS_CHOICES = (
        (DELIVERED, "Delivered"),
        (DELIVERY_FAILURE, "Delivery Failure"),
        (INACTIVE_DEVICE, "Inactive Device"),
        (OPTED_OUT, "Opted Out"),
        (RETRY, "Retry"),
        (SCHEDULED, "Scheduled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_target = models.ForeignKey(
        UserTarget, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=100)
    body = models.TextField()
    extra = models.JSONField(blank=True, null=True, default=dict)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    scheduled_delivery = models.DateTimeField()
    attempted_delivery = models.DateTimeField(null=True, blank=True)
    retry_time_interval = models.PositiveIntegerField(default=0)
    retry_attempts = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)

    class Meta:
        db_table = "notification_system_notification"
        verbose_name_plural = "Notifications"
        unique_together = [
            "user_target",
            "scheduled_delivery",
            "title",
            "extra",
        ]

    def __str__(self):
        return "{} - {} - {}".format(
            self.user_target.user.username, self.status, self.scheduled_delivery
        )

    def clean(self):
        """
        Perform a few data checks whenever an instance is saved.

        1. Don't allow notifications with an attempted delivery date to
           have a status of 'SCHEDULED'.
        2. If a notification has a status other than 'SCHEDULED' it MUST
           have an attempted delivery date.
        3. Don't allow notifications to be saved if the user has opted out.

        Raises
        ------
        ValidationError
            Will include details of what caused the validation error.
        """
        opted_out = (
            hasattr(self.user_target.user, "notification_opt_out")
            and self.user_target.user.notification_opt_out.has_opted_out
        )
        if opted_out:
            raise ValidationError("This user has opted out of Notifications.")

        if self.attempted_delivery and self.status == "SCHEDULED":
            raise ValidationError(
                "Status cannot be 'SCHEDULED' if there is an attempted delivery."
            )

        if self.attempted_delivery and self.status != "SCHEDULED":
            raise ValidationError(
                "Attempted Delivery must be filled out if Status is {}".format(
                    self.status
                )
            )
