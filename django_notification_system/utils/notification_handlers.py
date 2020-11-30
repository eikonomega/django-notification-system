import logging

import html2text
import socket
from dateutil.relativedelta import relativedelta

from smtplib import SMTPException

import django.core.mail
from django.conf import settings
from django.utils import timezone
from requests import HTTPError

from exponent_server_sdk import PushClient, PushMessage, PushResponseError, PushServerError, DeviceNotRegisteredError, PushResponse
from sentry_sdk import capture_exception

from website.notifications.models import Notification
from website.utils.logging_utils import generate_extra

logger = logging.getLogger(__name__)

def check_and_update_retry_attempts(notification, minute_interval=None):
    """
    Check if the retry_attempt and max_retries are equal.
    If they are we want to change the status to DELIVERY_FAILURE.
    If not, we want to RETRY at a given minute interval.
    """
    if notification.max_retries != notification.retry_attempts:
        notification.retry_attempts += 1
        notification.save()
        # We have to go deeper...
        if notification.max_retries != notification.retry_attempts:
            notification.status = notification.RETRY
            if minute_interval is not None:
                notification.scheduled_delivery = timezone.now(
                )+relativedelta(minutes=minute_interval)
            else:
                notification.scheduled_delivery = timezone.now(
                )+relativedelta(minutes=notification.retry_time_interval)
            notification.attempted_delivery = timezone.now()
            notification.save()

        else:
            notification.status = notification.DELIVERY_FAILURE
            notification.attempted_delivery = timezone.now()
            notification.save()


def prepare_extra(extra: dict):
    """
    Take in a JSON object from the Notification model instance and prepare a dictionary with all
    options available for PushMessage(). Loop through expected push_options and if the option
    exists in 'extra' JSON then it gets added to the dict with its value or else it gets added
    to the dictionary with None as its value.

    Parameters
    ----------
    extra
        JSON from the Notification model instance field 'extra'

    Returns
    -------
    Dictionary consisting of PushMessage() options
    """
    final_extra = {}
    push_options = ['data', 'sound', 'ttl',
                    'expiration', 'priority', 'badge', 'channel_id']
    for item in push_options:
        try:
            final_extra[item] = extra[item]
        except (KeyError, TypeError):
            final_extra[item] = None
    return final_extra


def send_push_message(notification: Notification):
    """
    Push notifications to the target device using the exponent_server_sdk library.

    Parameters
    ----------
    notification : obj
        The Notification object to be sent.
    extra : dict
        Extra options that can be added to the notification that aren't required (sound, ttl, etc.)

    Returns
    -------
    Returns two values:
        - Error/Success message
    """
    extra = prepare_extra(notification.extra)

    try:
        response = PushClient().publish(
            PushMessage(to=str(notification.user_target.user_target_id),
                        title=notification.title,
                        body=notification.body,
                        data=extra['data'],
                        sound=extra['sound'],
                        ttl=extra['ttl'],
                        expiration=extra['expiration'],
                        priority=extra['priority'],
                        badge=extra['badge'],
                        channel_id=extra['channel_id']))
    except (PushServerError, HTTPError, ValueError) as e:
        check_and_update_retry_attempts(notification)
        capture_exception(e)
        logger.error("Error sending push message", exc_info=e)
        return("{}: {}".format(type(e), e))
    return handle_push_response(notification, response)


def handle_push_response(notification: Notification, response: PushResponse):
    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError as e:
        user_target = notification.user_target
        user_target.active = False
        user_target.save()
        logger.info(
            "Deactivated user target %s"
            "because Expo/Firebase/Google reported device not registered",
            user_target,
            extra=generate_extra(
                user_target=user_target,
            )
        )
        return "{}: {}".format(type(e), e)
    except PushResponseError as e:
        check_and_update_retry_attempts(notification)
        capture_exception(e)
        logger.error(
            "Error validating response from push message",
             exc_info=e,
             extra=generate_extra(
                 notification=notification,
                 push_response__message=e.message,
                 push_response=e.push_response,
             )
         )
        return "{}: {}".format(type(e), e)
    else:
        notification.status = notification.DELIVERED
        notification.attempted_delivery = timezone.now()
        notification.save()
        return('Notification Successfully Pushed!')


def send_email(notification):
    """
    Email notifications to the target device using the smtp.nd.edu server.

    Parameters
    ----------
    notification : obj
        The Notification object to be sent.

    Returns
    -------
    Returns two values:
        - Error/Success message
    """
    try:
        django.core.mail.send_mail(
            subject=notification.title,
            message=html2text.html2text(notification.body),
            html_message=notification.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user_target.user_target_id],
            fail_silently=False)

    except SMTPException as e:
        # Update the notification to retry tomorrow if we are not at the
        # max amount of retries. SMTPEXceptions are usually the result of
        # hitting our daily limit of emails.
        check_and_update_retry_attempts(notification)
        return('Email could not be sent: {}'.format(e))

    except socket.error as se:
        # Update the notification to retry in 90 minutes if we are not at the
        # max amount of retries. Socket errors are rare, sporadic and
        # inconsistent but usually resolved relatively quickly
        check_and_update_retry_attempts(notification, 90)
        return('Email could not be sent: {}'.format(se))

    # If everything is fine, we update the notification
    # to DELIVERED
    notification.status = notification.DELIVERED
    notification.attempted_delivery = timezone.now()
    notification.save()
    return('Email Successfully Sent')
