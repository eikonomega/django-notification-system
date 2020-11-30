from collections import namedtuple
from exponent_server_sdk import PushResponseError, DeviceNotRegisteredError, MessageTooBigError, MessageRateExceededError, PushServerError, PushMessage, PushResponse


class MockPushClient(object):
    """Exponent push client

    See full API docs at https://docs.expo.io/versions/latest/guides/push-notifications.html#http2-api
    """
    DEFAULT_HOST = "https://exp.host" # TODO
    DEFAULT_BASE_API_URL = "/--/api/v2"

    def __init__(self, host=None, api_url=None):
        """Construct a new PushClient object.

        Args:
            host: The server protocol, hostname, and port.
            api_url: The api url at the host.
        """
        self.host = host
        if not self.host:
            self.host = MockPushClient.DEFAULT_HOST

        self.api_url = api_url
        if not self.api_url:
            self.api_url = MockPushClient.DEFAULT_BASE_API_URL

    @classmethod
    def is_exponent_push_token(cls, token):
        """Returns `True` if the token is an Exponent push token"""
        import six

        return (
            isinstance(token, six.string_types) and
            token.startswith('ExponentPushToken'))

    def _publish_internal(self, push_messages):
        """Send push notifications

        The server will validate any type of syntax errors and the client will
        raise the proper exceptions for the user to handle.

        Each notification is of the form:
        {
          'to': 'ExponentPushToken[xxx]',
          'body': 'This text gets display in the notification',
          'badge': 1,
          'data': {'any': 'json object'},
        }

        Args:
            push_messages: An array of PushMessage objects.
        """
        receipts = []
        for i, message in enumerate(push_messages):
            payload = message.get_payload()
            receipts.append(PushResponse(
                push_message=message,
                status=PushResponse.SUCCESS_STATUS,
                message='',
                details=None))
            if payload.get('sound', 'default') != 'default':
                raise PushServerError('Request failed', {})

        return receipts

    def publish(self, push_message):
        """Sends a single push notification

        Args:
            push_message: A single PushMessage object.

        Returns:
           A PushResponse object which contains the results.
        """
        return self.publish_multiple([push_message])[0]

    def publish_multiple(self, push_messages):
        """Sends multiple push notifications at once

        Args:
            push_messages: An array of PushMessage objects.

        Returns:
           An array of PushResponse objects which contains the results.
        """
        return self._publish_internal(push_messages)
