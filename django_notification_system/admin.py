"""Admin interface setup for Notifications feature/app"""

from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Notification, OptOut, Target, UserTarget
from .utils.opt_out_link import get_opt_out_link
from .utils.admin_site_utils import (
    MeOrAllFilter,
    is_null_filter_factory,
    USER_SEARCH_FIELDS,
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "user_target",
        "status",
        "scheduled_delivery",
        "attempted_delivery",
    ]
    list_filter = [
        "status",
        is_null_filter_factory("attempted_delivery"),
        "user_target__target",
    ]

    search_fields = [
        "user_target__" + field for field in USER_SEARCH_FIELDS
    ] + ["title", "body"]

    autocomplete_fields = ["user_target"]


@admin.register(OptOut)
class OptOutAdmin(admin.ModelAdmin):
    list_display = ["user", "active"]
    autocomplete_fields = ["user"]
    search_fields = USER_SEARCH_FIELDS


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ["name", "notification_module_name"]


@admin.register(UserTarget)
class UserTargetAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "target",
        "description",
        "target_user_id",
        "active",
    ]

    list_filter = ["active", MeOrAllFilter, "target"]

    search_fields = USER_SEARCH_FIELDS + (
        "target_user_id",
        "description",
    )
