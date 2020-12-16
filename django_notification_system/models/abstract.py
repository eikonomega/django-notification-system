"""Application Wide Abstract Model Definitions"""

from django.db import models


class CreatedModifiedAbstractModel(models.Model):
    """
    Abstract base model that is used to add `created_date`
    and `modified_date` fields to all descendant models.
    """

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True