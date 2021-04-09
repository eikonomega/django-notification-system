from django.core.management.base import BaseCommand

from ...utils.sender import Sender


class Command(BaseCommand):
    """
    Push all SCHEDULED notifications with a scheduled_delivery before the current date_time
    """

    help = __doc__

    def handle(self, *args, **options):
        sender = Sender()
        sender.execute(verbose=True)
