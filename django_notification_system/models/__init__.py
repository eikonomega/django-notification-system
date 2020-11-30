"""
This package contains all model definitions for the Django Notification System.
As a convience, the models are made available directly on the package namespace.
"""

from .notification import Notification
from .opt_out import OptOut
from .target import Target
from .user_target import UserTarget

__all__ = [
    "OptOut",
    "Target",
    "UserTarget",
    "Notification",
]
