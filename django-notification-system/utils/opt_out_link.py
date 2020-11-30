from django.contrib.auth.models import User
from django.urls import reverse

from ..models import OptOut


def get_opt_out_link(user: User):
    # Get or create returns a tuple, so we want the object
    opt_out = OptOut.objects.get_or_create(user=user)[0]
    return reverse('unsubscribe') + f"?u={opt_out.id}"
