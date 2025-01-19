from django.contrib import admin
from apps.general.models import (
    User, Profile, Invoice, Measurement, Notification, 
    NotificationSettings, InvoiceComparison, EmailVerification, 
    UploadLog, ReminderSchedule
)

class UserAdmin(admin.ModelAdmin):
    fields = ['dni', 'fullname', 'email', 'is_staff', 'is_superuser', 'is_active', 'created_at', 'updated_at']
    list_display = ['user_id', 'dni', 'fullname', 'email', 'is_staff', 'is_superuser', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['dni', 'fullname', 'email']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(User, UserAdmin)

class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'birth_date', 'address', 'phone_number', 'photo', 'created_at', 'updated_at']
    list_display = ['profile_id', 'user', 'birth_date', 'address', 'phone_number', 'photo','created_at', 'updated_at']
    search_fields = ['user__dni', 'user__fullname']
    list_filter = ['birth_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(Profile, ProfileAdmin)

from django.utils.safestring import mark_safe
import json

def format_json_field(obj, field_name):
    try:
        json_data = getattr(obj, field_name, {})
        pretty_data = json.dumps(json_data, indent=2)
        return mark_safe(f'<pre>{pretty_data}</pre>')
    except (TypeError, ValueError):
        return "Invalid JSON"

class InvoiceAdmin(admin.ModelAdmin):
    fields = ['user', 'billing_period_start', 'billing_period_end', 'data', 'image_url', 'created_at', 'updated_at']
    list_display = ['id', 'user', 'billing_period_start', 'billing_period_end', 'display_data', 'image_url', 'created_at', 'updated_at']
    search_fields = ['user__dni', 'user__fullname']
    list_filter = ['billing_period_start', 'billing_period_end']
    readonly_fields = ['created_at', 'updated_at']

    def display_data(self, obj):
        return format_json_field(obj, 'data')

    display_data.short_description = "Invoice Data"

admin.site.register(Invoice, InvoiceAdmin)

class MeasurementAdmin(admin.ModelAdmin):
    fields = ['user', 'measurement_start', 'measurement_end', 'data', 'created_at', 'updated_at']
    list_display = ['id', 'user', 'measurement_start', 'measurement_end', 'display_data', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']

    def display_data(self, obj):
        return format_json_field(obj, 'data')

    display_data.short_description = "Measurement Data"

admin.site.register(Measurement, MeasurementAdmin)


class NotificationAdmin(admin.ModelAdmin):
    fields = ['notification_id', 'user', 'type', 'message', 'is_read', 'created_at']
    list_display = ['notification_id', 'user', 'type', 'message', 'is_read', 'created_at']
    list_filter = ['type', 'is_read']
    readonly_fields = ['notification_id', 'created_at']

admin.site.register(Notification, NotificationAdmin)

class NotificationSettingsAdmin(admin.ModelAdmin):
    fields = [
        'user', 
        'enable_alerts', 
        'enable_recommendations', 
        'enable_reminders',
        'created_at', 
        'updated_at'
    ]
    list_display = [
        'notification_setting_id', 
        'user', 
        'enable_alerts', 
        'enable_recommendations', 
        'enable_reminders',
        'created_at', 
        'updated_at'
    ]
    search_fields = ['user__dni', 'user__fullname']
    list_filter = ['enable_alerts', 'enable_recommendations', 'enable_reminders']
    readonly_fields = ['notification_setting_id', 'created_at', 'updated_at']

admin.site.register(NotificationSettings, NotificationSettingsAdmin)


class InvoiceComparisonAdmin(admin.ModelAdmin):
    fields = ['user', 'invoice', 'measurement', 'comparison_results', 'is_comparison_valid', 'created_at', 'updated_at']
    list_display = ['id', 'user', 'invoice', 'measurement', 'display_comparison_results', 'is_comparison_valid', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']

    def display_comparison_results(self, obj):
        return format_json_field(obj, 'comparison_results')

    display_comparison_results.short_description = "Comparison Results (JSON)"

admin.site.register(InvoiceComparison, InvoiceComparisonAdmin)


class EmailVerificationAdmin(admin.ModelAdmin):
    fields = ['email', 'masked_verification_code', 'code_expiration', 'is_used', 'attempts', 'created_at']
    list_display = ['email', 'masked_verification_code', 'code_expiration', 'is_used', 'attempts', 'created_at']
    readonly_fields = ['masked_verification_code', 'created_at']
    search_fields = ['email']
    list_filter = ['is_used', 'code_expiration', 'created_at']

    def masked_verification_code(self, obj):
        if obj.verification_code:
            # Mask the hashed code with asterisks except for the last 4 characters
            return f"{'*' * (len(obj.verification_code) - 4)}{obj.verification_code[-4:]}"
        return "No Code Set"

    masked_verification_code.short_description = "Verification Code (Masked)"

admin.site.register(EmailVerification, EmailVerificationAdmin)


class UploadLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'file_name', 'file_size', 'file_hash', 'timestamp']
    search_fields = ['user__fullname','file_name']
    list_filter = ['timestamp',]
    ordering = ['-timestamp',]
    readonly_fields = ['file_hash', 'timestamp']

admin.site.register(UploadLog, UploadLogAdmin)


@admin.register(ReminderSchedule)
class ReminderScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'invoice_comparison', 'scheduled_time')
    list_filter = ('scheduled_time',)
    search_fields = ('user__email', 'invoice_comparison__id')
    ordering = ('-scheduled_time',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['user', 'invoice_comparison', 'scheduled_time']
        return []
