import html2text
import socket
from smtplib import SMTPException

import django.core.mail
from django.conf import settings
from django.utils import timezone

from ..utils import check_and_update_retry_attempts


def send_notification(notification):
    """
    Send email notifications to the target device using the email server.

    Args:
        notification (Notification): The email notification to be sent.

    Returns:
        str: Whether the email has successfully sent, or an error message.
    """
    try:
        django.core.mail.send_mail(
            subject=notification.title,
            message=html2text.html2text(notification.body),
            html_message=notification.body,
            from_email=settings.NOTIFICATION_SYSTEM_TARGETS['email']['from_email'],
            recipient_list=[notification.target_user_record.target_user_id],
            fail_silently=False,
        )

    except SMTPException as e:
        # Update the notification to retry tomorrow if we are not at the
        # max amount of retries. SMTPEXceptions are usually the result of
        # hitting our daily limit of emails.
        check_and_update_retry_attempts(notification)
        return "Email could not be sent: {}".format(e)

    except socket.error as se:
        # Update the notification to retry in 90 minutes if we are not at the
        # max amount of retries. Socket errors are rare, sporadic and
        # inconsistent but usually resolved relatively quickly
        check_and_update_retry_attempts(notification, 90)
        return "Email could not be sent: {}".format(se)

    # If everything is fine, we update the notification
    # to DELIVERED
    notification.status = notification.DELIVERED
    notification.attempted_delivery = timezone.now()
    notification.save()
    return "Email Successfully Sent"
