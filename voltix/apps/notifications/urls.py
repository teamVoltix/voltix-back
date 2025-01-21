from django.urls import path
from .views import NotificationSettingsRetrieveView, NotificationSettingsUpdateView

urlpatterns = [
    # Retrieve notification settings
    path('', NotificationSettingsRetrieveView.as_view(), name='notification-settings-retrieve'),

    # Update notification settings
    path('update/', NotificationSettingsUpdateView.as_view(), name='notification-settings-update'),
]

