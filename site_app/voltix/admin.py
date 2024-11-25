from django.contrib import admin
from .models import (
    User, Profile, Invoice, Measurement, Notification, 
    NotificationSettings, InvoiceComparison, MiLuzBase, Token
)

class UserAdmin(admin.ModelAdmin):
    fields = ['dni', 'fullname', 'email', 'is_staff', 'is_superuser', 'is_active', 'created_at', 'updated_at']
    list_display = ['user_id', 'dni', 'fullname', 'email', 'is_staff', 'is_superuser', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['dni', 'fullname', 'email']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(User, UserAdmin)

# Register other models
class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'birth_date', 'address', 'phone_number', 'preferences', 'created_at', 'updated_at']
    list_display = ['profile_id', 'user', 'birth_date', 'address', 'phone_number', 'created_at', 'updated_at']
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
    fields = ['user', 'billing_period_start', 'billing_period_end', 'data', 'created_at', 'updated_at']
    list_display = ['id', 'user', 'billing_period_start', 'billing_period_end', 'display_data', 'created_at', 'updated_at']
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
    fields = ['notification_id', 'user', 'message', 'is_read', 'created_at']
    list_display = ['notification_id', 'user', 'message', 'is_read', 'created_at']
    readonly_fields = ['created_at']

admin.site.register(Notification, NotificationAdmin)

class InvoiceComparisonAdmin(admin.ModelAdmin):
    fields = ['user', 'invoice', 'measurement', 'comparison_results', 'is_comparison_valid', 'created_at', 'updated_at']
    list_display = ['id', 'user', 'invoice', 'measurement', 'display_comparison_results', 'is_comparison_valid', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']

    def display_comparison_results(self, obj):
        return format_json_field(obj, 'comparison_results')

    display_comparison_results.short_description = "Comparison Results (JSON)"

admin.site.register(InvoiceComparison, InvoiceComparisonAdmin)

class MiLuzBaseAdmin(admin.ModelAdmin):
    fields = ['user', 'billing_period_start', 'billing_period_end', 'expected_consumption', 'rate_per_kwh', 'fixed_charge', 'tax_rate', 'total_expected_cost']
    list_display = ['id', 'user', 'billing_period_start', 'billing_period_end', 'expected_consumption', 'rate_per_kwh', 'fixed_charge', 'tax_rate', 'total_expected_cost']
    readonly_fields = ['billing_period_start', 'billing_period_end']

admin.site.register(MiLuzBase, MiLuzBaseAdmin)

admin.site.register(Token)
