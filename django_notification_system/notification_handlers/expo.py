"""A Django Notification System Handler."""
from exponent_server_sdk import (
    PushClient,
    PushMessage,
    PushResponseError,
    PushServerError,
    DeviceNotRegisteredError,
)
from requests import HTTPError

from django.utils import timezone

from ..utils import check_and_update_retry_attempts


def send_notification(notification) -> str:
    """
    Send push notifications (Expo) to the target device using the Expo server.

    Args:
        notification (Notification): The Expo push notification to be sent.

    Returns:
        String: Whether the push notification has successfully sent, or an error message.
    """
    extra = prepare_extra(notification.extra)

    try:
        response = PushClient().publish(
            PushMessage(
                to=str(notification.target_user_record.target_user_id),
                title=notification.title,
                body=notification.body,
                data=extra["data"],
                sound=extra["sound"],
                ttl=extra["ttl"],
                expiration=extra["expiration"],
                priority=extra["priority"],
                badge=extra["badge"],
                channel_id=extra["channel_id"],
            )
        )
    except (PushServerError, HTTPError, ValueError) as e:
        check_and_update_retry_attempts(notification)
        return "{}: {}".format(type(e), e)

    return handle_push_response(notification, response)


def prepare_extra(extra):
    """
    Take in a JSON object from the Notification model instance and prepare a dictionary with all
    options available for PushMessage(). Loop through expected push_options and if the option
    exists in 'extra' JSON then it gets added to the dict with its value or else it gets added
    to the dictionary with None as its value.

    Args:
        extra (dict): JSON from the Notification model instance field 'extra'

    Returns:
        dict: Dictionary consisting of PushMessage() options
    """
    final_extra = {}
    push_options = [
        "data",
        "sound",
        "ttl",
        "expiration",
        "priority",
        "badge",
        "channel_id",
    ]
    for item in push_options:
        try:
            final_extra[item] = extra[item]
        except (KeyError, TypeError):
            final_extra[item] = None
    return final_extra


def handle_push_response(notification, response):
    """
    This function handles the push response requested in send_expo()

    Args:
        notification (Notification): The Expo push notification to be sent.
        response (PushResponse): The Expo push response

    Returns:
        str: Whether the push has successfully sent, or an error message.
    """
    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError as e:
        target_user_record = notification.target_user_record
        target_user_record.active = False
        target_user_record.save()
        return "{}: {}".format(type(e), e)
    except PushResponseError as e:
        check_and_update_retry_attempts(notification)
        return "{}: {}".format(type(e), e)
    else:
        notification.status = notification.DELIVERED
        notification.attempted_delivery = timezone.now()
        notification.save()
        return "Notification Successfully Pushed!"
