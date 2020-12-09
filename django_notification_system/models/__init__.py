"""
This package contains all model definitions for the Django Notification System.
As a convience, the models are made available directly on the package namespace.
"""

from .notification import Notification
from .opt_out import NotificationOptOut
from .target import NotificationTarget
from .target_user_record import TargetUserRecord

__all__ = [
    "NotificationOptOut",
    "NotificationTarget",
    "TargetUserRecord",
    "Notification",
]
