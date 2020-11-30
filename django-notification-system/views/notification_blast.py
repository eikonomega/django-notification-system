import time
from datetime import timedelta

from django import forms
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from ..models import Notification, UserTarget
from ...database_apps.referral_code_manager.models import ReferralCode


class NotificationBlastForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput)
    body = forms.CharField(widget=forms.Textarea, required=False)
    referral_code = forms.ModelChoiceField(
        required=False,
        queryset=ReferralCode.objects.order_by("code")
    )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class NotificationBlasterView(UserPassesTestMixin, View):
    """
        A view where superusers can send out a notification blast to all active Expo User Targets.
    """

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request):
        start_time = time.time()

        # create a form instance and populate it with data from the request:
        form = NotificationBlastForm(request.POST)
        if not form.is_valid():
            raise ValidationError(form.errors)

        title = form.cleaned_data["title"]
        body = form.cleaned_data["body"]
        referral_code = form.cleaned_data["referral_code"]
        now = timezone.now()
        notification_list = []

        usertarget_set = UserTarget.objects.filter(
            active=True, target__class_name="Expo"
        )

        if referral_code is not None:
            usertarget_set = usertarget_set.filter(
                user__portaluser__subject__referral_code=referral_code
            )

        for i, user_target in enumerate(usertarget_set):
            user = user_target.user
            opted_out = (
                    hasattr(user, "notification_opt_out")
                    and user.notification_opt_out.has_opted_out
            )

            if not opted_out:
                notification_list.append(
                    Notification(
                        user_target=user_target,
                        title=title,
                        body=body,
                        # extra=extra,
                        status=Notification.SCHEDULED,
                        scheduled_delivery=now + timedelta(seconds=i),
                    )
                )

        Notification.objects.bulk_create(notification_list)
        end_time = time.time()

        # makes it take longer to give more gravity
        time.sleep(max(1.0 - (end_time - start_time), 0.0))
        return HttpResponseRedirect(reverse("notifications_blasted"))

    def get(self, request):

        form = NotificationBlastForm()
        context = {"form": form}
        return render(request, "notifications/notification_blaster.html", context)


class NotificationsBlastedView(View):
    def get(self, request):
        return render(request, "notifications/notifications_blasted.html")
