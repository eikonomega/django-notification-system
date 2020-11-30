from .views.notification_blast import (
    NotificationBlasterView,
    NotificationsBlastedView,
)

from django.urls import path


urlpatterns = [
    path(
        "notification_blaster/",
        NotificationBlasterView.as_view(),
        name="notification_blaster",
    ),
    path(
        "notifications_blasted/",
        NotificationsBlastedView.as_view(),
        name="notifications_blasted",
    ),
]
