import logging

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from ..models.opt_out import NotificationOptOut
from ..utils.opt_out_link import get_opt_out_link
from ...utils.logging_utils import generate_extra

logger = logging.getLogger(__name__)

class OptOutForm(forms.Form):
    opt_out_uuid = forms.UUIDField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        opt_out_uuid = cleaned_data.get('opt_out_uuid')
        if not NotificationOptOut.objects.filter(id=opt_out_uuid):
            logger.error("invalid opt out id")
            raise ValidationError('Bad Opt Out ID')
        else:
            return cleaned_data

class OptOutView(View):
    """
        A view where users can opt in or out of all notifications
        Opt out links are generated using the utility method get_opt_out_link(user)
    """

    def post(self, request):
        # create a form instance and populate it with data from the request:
        form = OptOutForm(request.POST)
        if not form.is_valid():
            raise ValidationError(form.errors)
        opt_out = NotificationOptOut.objects.get(id=form.cleaned_data['opt_out_uuid'])
        opt_out.has_opted_out = not opt_out.has_opted_out
        opt_out.save() # save deletes all pending notifications!
        logger.info(
            "User %s opted out of notifications",
            opt_out.user,
            extra=generate_extra(
                event_code="USER_NOTIFICATION_OPT_OUT",
                request=request,
                user=opt_out.user,
            )
        )
        return HttpResponseRedirect(reverse('unsubscribe') + f"?u={opt_out.id}")

    def get(self, request):
        opt_out_uuid = request.GET.get('u')
        form = OptOutForm({'opt_out_uuid': opt_out_uuid})
        if not form.is_valid():
            # try to send user to the correct opt out link
            if request.user.is_authenticated:
                return redirect(get_opt_out_link(request.user))
            # else bump them to the home page
            # TODO: create a view where users can request to be emailed a new opt-out link
            return redirect("portal2.landing_page")

        opt_out = NotificationOptOut.objects.get(id=opt_out_uuid)
        user = opt_out.user
        context = {
            'form': form,
            'email': user.email,
            'has_opted_out': opt_out.has_opted_out,
        }
        return render(request, 'notifications/opt_out.html', context)
