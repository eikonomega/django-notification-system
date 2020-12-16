"""Custom exceptions for Django Notification System App."""


class NotificationSystemError(Exception):
    """Parent class for custom exceptions."""

    pass


class NotificationsNotCreated(NotificationSystemError):
    """Exception to raise when one or more notifications cannot be created."""

    pass


class NotificationNotSent(NotificationSystemError):
    """
    Exception to raise when a notification is not able
    to be sent, but we do not have a more specific cause.
    """

    pass


class UserIsOptedOut(NotificationNotSent):
    """
    Exception to raise when a notification is not able to
    be sent because the user is opted out.
    """

    def __init__(self):
        super().__init__("User is opted out")


class UserHasNoTargetRecords(NotificationNotSent):
    """
    Exception to raise when a notification is not able to
    be sent because the user has no available targets.
    """

    def __init__(self):
        super().__init__("User has no active targets")