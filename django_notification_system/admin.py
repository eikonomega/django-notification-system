"""Admin interface setup for Notifications feature/app"""

from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Notification,
    NotificationOptOut,
    NotificationTarget,
    TargetUserRecord,
)
from .utils.admin_site_utils import (
    MeOrAllFilter,
    is_null_filter_factory,
    USER_SEARCH_FIELDS,
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "target_user_record",
        "status",
        "scheduled_delivery",
        "attempted_delivery",
    ]
    list_filter = [
        "status",
        is_null_filter_factory("attempted_delivery"),
        "target_user_record__target",
    ]

    search_fields = [
        "target_user_record__" + field for field in USER_SEARCH_FIELDS
    ] + ["title", "body"]

    autocomplete_fields = ["target_user_record"]


@admin.register(NotificationOptOut)
class NotificationOptOutAdmin(admin.ModelAdmin):
    list_display = ["user", "active"]
    autocomplete_fields = ["user"]
    search_fields = USER_SEARCH_FIELDS


@admin.register(NotificationTarget)
class NotificationTargetAdmin(admin.ModelAdmin):
    list_display = ["name", "notification_module_name"]


@admin.register(TargetUserRecord)
class UserInNotificationTargetAdmin(admin.ModelAdmin):
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
