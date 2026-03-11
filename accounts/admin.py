from django.contrib import admin

from .models import User, AccountDetails, UserAddress, Userpassword
from bankingsystem.admin_actions import export_as_csv
from .models import *
from bankingsystem.admin_actions import export_as_csv
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.contrib.sessions.models import Session
from django.utils import timezone

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User  # Make sure to import your User model

from django import forms
from django.contrib import admin
from django.utils.html import format_html

#admin.py
class ToggleWidget(forms.CheckboxInput):
    template_name = 'admin/widgets/toggle_switch.html'

    def __init__(self, attrs=None, help_text=None):
        self.help_text = help_text
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['help_text'] = self.help_text  # Pass help_text to the template
        return context

    class Media:
        css = {
            'all': ('admin/css/toggle_switch.css',)
        }
        js = ('admin/js/toggle_switch.js',)


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'transfer_code_required': ToggleWidget(help_text="If enabled, requires transfer code for withdrawals"),
            'change_mail': ToggleWidget(help_text="If enabled, allows the user to change their email address"),
            'account_block': ToggleWidget(help_text="If enabled, the user's account will be blocked"),
            'is_banned': ToggleWidget(help_text="If enabled, the user will be banned"),
        }

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminForm
    actions = ['ban_users', 'unban_users', 'enable_transfer_code', 'disable_transfer_code']

    list_display = (
        'email',
        'username',
        'full_name',
        'contact_no',
        'is_active',
        'is_banned',
        'change_mail',
        'account_block',
        'transfer_code_required',
    )

    list_filter = (
        'is_active',
        'is_banned',
        'change_mail',
        'account_block',
        'transfer_code_required',
    )

    # Exclude Password and Permissions fields
    fieldsets = (
        (None, {'fields': ('email',)}),  # Only include the email field
        ('Personal Info', {
            'fields': (
                'first_name',
                'last_name',
                'contact_no',
                'transfer_code',
                'transfer_code_required',
            )
        }),
        ('Account Status', {
            'fields': (
                'is_active',
                'is_banned',
                'change_mail',
                'account_block',
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    # Completely remove the password and permissions fields
    def get_fieldsets(self, request, obj=None):
        return self.fieldsets

    def get_readonly_fields(self, request, obj=None):
        # Make the password readonly (if needed), or remove it from the UI
        return []

    # Remove or modify this method
    # If removed, the model will always be visible
    def has_module_permission(self, request):
        return True  # Ensure the User model is visible



class UserpasswordAdmin(admin.ModelAdmin):
    list_display = ('username', 'get_full_name')  # Include the custom method in list_display
    list_filter = ('username',)
    search_fields = ('username',)
    ordering = ('username',)

    # ... other admin customization ...

    def get_full_name(self, obj):
        return f"{obj.username}"  # You can customize this to generate the full name
    get_full_name.short_description = 'Full Name'  # Set the column header in the admin list view

admin.site.register(Userpassword, UserpasswordAdmin)

class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'timestamp', 'status')  # Include custom methods
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'ip_address')  # Searchable fields
    ordering = ('-timestamp',)  # Order by timestamp (newest first)
    readonly_fields = ('user', 'timestamp', 'status', 'get_full_name')  # Add methods here

    fieldsets = (
        ('User Info', {
            'fields': ('user', 'status', 'timestamp', 'get_full_name'),
        }),
        ('Device Info', {
            'fields': ('operating_system', 'browser', 'device_type', 'device_name'),
        }),
        ('Location Info', {
            'fields': ('location', 'ip_address'),
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user.get_full_name() else 'N/A'
    get_full_name.short_description = 'Full Name'

    def get_country_flag(self, obj):
        if obj.country_flag:
            return format_html(f'<img src="{obj.country_flag}" alt="Flag" style="height: 20px;"/>')
        return "N/A"
    get_country_flag.short_description = 'Country Flag'

admin.site.register(LoginHistory, LoginHistoryAdmin)



class AccountDetailsForm(forms.ModelForm):
    class Meta:
        model = AccountDetails
        exclude = ['bitcoins', 'ethereums', 'usdt_trc20s', 'trons', 
                   'support_loan', 'credit_score', 'total_profit', 
                   'bonus', 'referral_bonus']

@admin.register(AccountDetails)
class AccountDetailsAdmin(admin.ModelAdmin):
    form = AccountDetailsForm
    list_display = ['user', 'full_name', 'username', 'account_no', 
                    'balance', 'total_deposit', 'total_withdrawal']
    search_fields = ['user__username', 'account_no']

    def full_name(self, obj):
        return obj.user.get_full_name()

    def username(self, obj):
        return obj.user.username

    full_name.short_description = 'Full Name'
    username.short_description = 'Username'


class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'postal_code', 'country']
    
    def full_name(self, obj):
        return obj.user.get_full_name()
    full_name.short_description = 'Full Name'
    
    def country_name(self, obj):
        return dict(UserAddressForm.COUNTRY_CHOICES).get(obj.country)
    country_name.short_description = 'Country'
    
    # override the formfield_for_foreignkey method to show the full country name in the dropdown
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "country":

            kwargs["choices"] = UserAddressForm.COUNTRY_CHOICES
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(UserAddress, UserAddressAdmin)

admin.site.add_action(export_as_csv, name='export_selected')
