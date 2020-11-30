import uuid

from django.db import models

from website.abstract_models import CreatedModifiedAbstractModel


class Target(CreatedModifiedAbstractModel):
    """
    Definition of a Notification Target Model

    A target represents something that should receive a
    notication from our system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=15)
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
