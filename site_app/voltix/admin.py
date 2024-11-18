from django.contrib import admin
from .models import User, Profile, Invoice, Measurement, Notification, NotificationSettings, InvoiceComparison, MiLuzBase, Token

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    fields = ['user_id', 'dni', 'fullname', 'email', 'password', 'created_at', 'updated_at']
    list_display = ['user_id', 'dni', 'fullname', 'email', 'password', 'created_at', 'updated_at']

admin.site.register(User, UserAdmin)

class ProfileAdmin(admin.ModelAdmin):
    fields = ['profile_id', 'user', 'birth_date', 'address', 'phone_number', 'preferences', 'created_at', 'updated_at']
    list_display = ['profile_id', 'user', 'birth_date', 'address', 'phone_number', 'preferences', 'created_at', 'updated_at']

admin.site.register(Profile, ProfileAdmin)    

class InvoiceAdmin(admin.ModelAdmin):
    fields = ['invoice_id', 'user', 'upload_date', 'amount_due', 'due_date', 'provider', 'file_path', 'ocr_data', 'created_at', 'updated_at']
    list_display = ['invoice_id', 'user', 'upload_date', 'amount_due', 'due_date', 'provider', 'file_path', 'ocr_data', 'created_at', 'updated_at']

admin.site.register(Invoice, InvoiceAdmin)   

class MeasurementAdmin(admin.ModelAdmin):
    fields = ['measurement_id', 'user', 'date', 'value', 'type', 'created_at', 'updated_at']
    list_display = ['measurement_id', 'user', 'date', 'value', 'type', 'created_at', 'updated_at']

admin.site.register(Measurement, MeasurementAdmin)

class NotificationAdmin(admin.ModelAdmin):
    fields = ['notification_id', 'user', 'message', 'is_read', 'created_at']
    list_display = ['notification_id', 'user', 'message', 'is_read', 'created_at']

admin.site.register(Notification, NotificationAdmin)


class InvoiceComparisonAdmin(admin.ModelAdmin):
    fields = ['comparison_id', 'user', 'invoice1', 'invoice2', 'comparison_date', 'comparison_result']
    list_display = ['comparison_id', 'user', 'invoice1', 'invoice2', 'comparison_date', 'comparison_result']

admin.site.register(InvoiceComparison, InvoiceComparisonAdmin)


class MiLuzBaseAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'billing_period_start', 'billing_period_end', 'expected_consumption', 'rate_per_kwh', 'fixed_charge', 'tax_rate', 'total_expected_cost']
    list_display = ['id', 'user', 'billing_period_start', 'billing_period_end', 'expected_consumption', 'rate_per_kwh', 'fixed_charge', 'tax_rate', 'total_expected_cost']

admin.site.register(MiLuzBase, MiLuzBaseAdmin)