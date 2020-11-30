import uuid

from django.conf import settings
from django.db import models

from website.abstract_models import CreatedModifiedAbstractModel
from website.notifications.models import Notification


class OptOut(CreatedModifiedAbstractModel):
    """
    Definition of a User Opt-Out Model

    User's who have opted-out of communications should appear in this table.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_opt_out")  # todo kill related name
    has_opted_out = models.BooleanField(default=False)

    class Meta:
        db_table = 'notifications_opt_out'
        verbose_name_plural = 'Opt Outs'

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.has_opted_out:
            Notification.objects.filter(
                status=Notification.SCHEDULED,
                user_target__user=self.user).delete()
        super(OptOut, self).save(*args, **kwargs)
