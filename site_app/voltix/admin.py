# from django.contrib import admin
# from .models import User, Profile, Invoice, Measurement, Notification, NotificationSettings, InvoiceComparison, MiLuzBase, Token

# # Register your models here.

# class UserAdmin(admin.ModelAdmin):
#     # Fields to display in the admin form
#     fields = ['user_id', 'dni', 'fullname', 'email', 'is_staff', 'is_superuser', 'is_active', 'created_at', 'updated_at']
    
#     # Fields to display in the list view
#     list_display = ['user_id', 'dni', 'fullname', 'email', 'is_staff', 'is_superuser', 'is_active', 'created_at', 'updated_at']
    
#     # Fields to filter the list view
#     list_filter = ['is_staff', 'is_superuser', 'is_active']
    
#     # Fields to search in the admin interface
#     search_fields = ['dni', 'fullname', 'email']
    
#     # Read-only fields to prevent changes
#     readonly_fields = ['created_at', 'updated_at']

# admin.site.register(User, UserAdmin)

# class ProfileAdmin(admin.ModelAdmin):
#     fields = ['profile_id', 'user', 'birth_date', 'address', 'phone_number', 'preferences', 'created_at', 'updated_at']
#     list_display = ['profile_id', 'user', 'birth_date', 'address', 'phone_number', 'created_at', 'updated_at']
#     search_fields = ['user__dni', 'user__fullname']
#     list_filter = ['birth_date', 'created_at']
#     readonly_fields = ['created_at', 'updated_at']

# admin.site.register(Profile, ProfileAdmin)    

# class InvoiceAdmin(admin.ModelAdmin):
#     fields = ['invoice_id', 'user', 'upload_date', 'amount_due', 'due_date', 'provider', 'file_path', 'ocr_data', 'created_at', 'updated_at']
#     list_display = ['invoice_id', 'user', 'upload_date', 'amount_due', 'due_date', 'provider', 'created_at', 'updated_at']
#     search_fields = ['user__dni', 'user__fullname', 'provider']
#     list_filter = ['due_date', 'upload_date']
#     readonly_fields = ['created_at', 'updated_at']

# admin.site.register(Invoice, InvoiceAdmin)   

# class MeasurementAdmin(admin.ModelAdmin):
#     fields = ['measurement_id', 'user', 'date', 'value', 'type', 'created_at', 'updated_at']
#     list_display = ['measurement_id', 'user', 'date', 'value', 'type', 'created_at', 'updated_at']
#     readonly_fields = ['created_at', 'updated_at']

# class NotificationAdmin(admin.ModelAdmin):
#     fields = ['notification_id', 'user', 'message', 'is_read', 'created_at']
#     list_display = ['notification_id', 'user', 'message', 'is_read', 'created_at']
#     readonly_fields = ['created_at']


# class InvoiceComparisonAdmin(admin.ModelAdmin):
#     fields = ['comparison_id', 'user', 'invoice1', 'invoice2', 'comparison_date', 'comparison_result']
#     list_display = ['comparison_id', 'user', 'invoice1', 'invoice2', 'comparison_date', 'comparison_result']
#     readonly_fields = ['comparison_date']
#     readonly_fields = ['created_at']


# class MiLuzBaseAdmin(admin.ModelAdmin):
#     fields = ['id', 'user', 'billing_period_start', 'billing_period_end', 'expected_consumption', 'rate_per_kwh', 'fixed_charge', 'tax_rate', 'total_expected_cost']
#     list_display = ['id', 'user', 'billing_period_start', 'billing_period_end', 'expected_consumption', 'rate_per_kwh', 'fixed_charge', 'tax_rate', 'total_expected_cost']
#     readonly_fields = ['billing_period_start', 'billing_period_end']


# admin.site.register(User, UserAdmin)
# admin.site.register(Profile, ProfileAdmin)
# admin.site.register(Invoice, InvoiceAdmin)
# admin.site.register(Measurement, MeasurementAdmin)
# admin.site.register(Notification, NotificationAdmin)
# admin.site.register(NotificationSettings)
# admin.site.register(InvoiceComparison, InvoiceComparisonAdmin)
# admin.site.register(MiLuzBase, MiLuzBaseAdmin)
# admin.site.register(Token)


from django.contrib import admin
from .models import (
    User, Profile, Invoice, Measurement, Notification, 
    NotificationSettings, InvoiceComparison, MiLuzBase, Token
)

class UserAdmin(admin.ModelAdmin):
    fields = ['user_id', 'dni', 'fullname', 'email', 'is_staff', 'is_superuser', 'is_active', 'created_at', 'updated_at']
    list_display = ['user_id', 'dni', 'fullname', 'email', 'is_staff', 'is_superuser', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['dni', 'fullname', 'email']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(User, UserAdmin)

# Register other models
class ProfileAdmin(admin.ModelAdmin):
    fields = ['profile_id', 'user', 'birth_date', 'address', 'phone_number', 'preferences', 'created_at', 'updated_at']
    list_display = ['profile_id', 'user', 'birth_date', 'address', 'phone_number', 'created_at', 'updated_at']
    search_fields = ['user__dni', 'user__fullname']
    list_filter = ['birth_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(Profile, ProfileAdmin)

# class InvoiceAdmin(admin.ModelAdmin):
#     fields = ['invoice_id', 'user', 'upload_date', 'amount_due', 'due_date', 'provider', 'file_path', 'ocr_data', 'created_at', 'updated_at']
#     list_display = ['invoice_id', 'user', 'upload_date', 'amount_due', 'due_date', 'provider', 'created_at', 'updated_at']
#     search_fields = ['user__dni', 'user__fullname', 'provider']
#     list_filter = ['due_date', 'upload_date']
#     readonly_fields = ['created_at', 'updated_at']

# admin.site.register(Invoice, InvoiceAdmin)

class InvoiceAdmin(admin.ModelAdmin):
    fields = [
        'id', 'user', 'billing_period_start', 'billing_period_end', 
        'price_per_kwh', 'data', 'created_at', 'updated_at'
    ]
    list_display = [
        'id', 'user', 'billing_period_start', 'billing_period_end', 
        'price_per_kwh', 'created_at', 'updated_at'
    ]
    search_fields = ['user__dni', 'user__fullname']
    list_filter = ['billing_period_start', 'billing_period_end']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(Invoice, InvoiceAdmin)

# class MeasurementAdmin(admin.ModelAdmin):
#     fields = ['measurement_id', 'user', 'date', 'value', 'type', 'created_at', 'updated_at']
#     list_display = ['measurement_id', 'user', 'date', 'value', 'type', 'created_at', 'updated_at']
#     readonly_fields = ['created_at', 'updated_at']

# admin.site.register(Measurement, MeasurementAdmin)

class MeasurementAdmin(admin.ModelAdmin):
    fields = [
        'id', 'user', 'date', 'value', 'data', 
        'created_at', 'updated_at'
    ]
    list_display = [
        'id', 'user', 'date', 'value', 'created_at', 'updated_at'
    ]
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(Measurement, MeasurementAdmin)


class NotificationAdmin(admin.ModelAdmin):
    fields = ['notification_id', 'user', 'message', 'is_read', 'created_at']
    list_display = ['notification_id', 'user', 'message', 'is_read', 'created_at']
    readonly_fields = ['created_at']

admin.site.register(Notification, NotificationAdmin)

# class InvoiceComparisonAdmin(admin.ModelAdmin):
#     fields = ['id', 'user', 'invoice', 'comparison_date', 'comparison_result']
#     list_display = ['comparison_id', 'user', 'invoice1', 'invoice2', 'comparison_date', 'comparison_result']
#     readonly_fields = ['comparison_date']

# admin.site.register(InvoiceComparison, InvoiceComparisonAdmin)

class InvoiceComparisonAdmin(admin.ModelAdmin):
    fields = [
        'id', 'user', 'invoice', 'measurement', 
        'comparison_date', 'comparison_results', 'is_comparison_valid'
    ]
    list_display = [
        'id', 'user', 'invoice', 'measurement', 
        'comparison_date', 'is_comparison_valid'
    ]
    readonly_fields = ['comparison_date']

admin.site.register(InvoiceComparison, InvoiceComparisonAdmin)

class MiLuzBaseAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'billing_period_start', 'billing_period_end', 'expected_consumption', 'rate_per_kwh', 'fixed_charge', 'tax_rate', 'total_expected_cost']
    list_display = ['id', 'user', 'billing_period_start', 'billing_period_end', 'expected_consumption', 'rate_per_kwh', 'fixed_charge', 'tax_rate', 'total_expected_cost']
    readonly_fields = ['billing_period_start', 'billing_period_end']

admin.site.register(MiLuzBase, MiLuzBaseAdmin)

admin.site.register(Token)
