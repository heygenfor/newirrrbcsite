
from django.contrib import admin

from .models import *
# Register your models here.
from django.utils.html import format_html

from django.db import models
import uuid
from bankingsystem.admin_actions import export_as_csv

from django import forms

from django.contrib import admin
from django.utils.html import format_html
from .models import LocalWithdrawal, PayPalWithdrawal, SkrillWithdrawal, RevolutWithdrawal, WiseWithdrawal

class BaseWithdrawalAdmin(admin.ModelAdmin):
    """Base admin class for all withdrawal types"""
    list_per_page = 50
    date_hierarchy = 'timestamp'
    list_filter = ['status', 'timestamp']
    readonly_fields = ['timestamp']
    
    def get_amount_display(self, obj):
        return f"${obj.amount:,.2f}"
    get_amount_display.short_description = 'Amount'
    
    def get_status_display(self, obj):
        status_colors = {
            'pending': 'orange',
            'completed': 'green',
            'cancelled': 'red',
            'declined': 'darkred'
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    get_status_display.short_description = 'Status'
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q

@admin.register(LocalWithdrawal)
class LocalWithdrawalAdmin(BaseWithdrawalAdmin):
    list_display = [
        'timestamp', 
        'user_link',
        'recipient_name',
        'recipient_account_number',
        'get_amount_display',
        'get_status_badge',
        'transaction_type',
        'created_time_ago'
    ]
    
    list_display_links = ['timestamp', 'recipient_name']
    
    search_fields = [
        'user__email', 
        'user__username',
        'user__first_name',
        'user__last_name',
        'recipient_name',
        'recipient_account_number',
        'recipient_email',
        'description',
        'id'
    ]
    
    list_filter = [
        'status',
        'transaction_type',
        ('timestamp', admin.DateFieldListFilter),
        'user',
    ] + BaseWithdrawalAdmin.list_filter
    
    readonly_fields = [
        'created_time_ago',
        'sender_name_display',
        'formatted_amount'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'sender_name_display', 'timestamp'),
            'description': 'Information about the user initiating the withdrawal'
        }),
        ('Recipient Details', {
            'fields': (
                'recipient_name', 
                'recipient_email', 
                'recipient_account_number'
            ),
            'description': 'Details of the withdrawal recipient'
        }),
        ('Transaction Details', {
            'fields': (
                'amount',
                'formatted_amount',
                'transaction_type',
                'description', 
                'status'
            ),
            'description': 'Transaction amount, type, and current status'
        }),
        ('Metadata', {
            'fields': ('created_time_ago',),
            'classes': ('collapse',),
            'description': 'Additional transaction metadata'
        }),
    )
    
    actions = [
        'mark_as_completed',
        'mark_as_cancelled',
        'mark_as_declined',
        'mark_as_pending'
    ]
    
    list_per_page = 25
    date_hierarchy = 'timestamp'
    
    # Custom display methods
    @admin.display(description='User', ordering='user__username')
    def user_link(self, obj):
        """Display clickable link to user's admin page"""
        try:
            # Get the correct app label and model name for User
            user_model = obj.user._meta
            url = reverse(
                f'admin:{user_model.app_label}_{user_model.model_name}_change',
                args=[obj.user.pk]
            )
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.user.username
            )
        except Exception:
            # Fallback to just displaying username if reverse fails
            return obj.user.username
    
    @admin.display(description='Amount', ordering='amount')
    def get_amount_display(self, obj):
        """Display formatted amount in list view"""
        formatted_amount = '₦{:,.2f}'.format(obj.amount)
        return format_html(
            '<strong style="color: #28A745;">{}</strong>',
            formatted_amount
        )
    
    @admin.display(description='Status')
    def get_status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': '#FFA500',     # Orange
            'completed': '#28A745',   # Green
            'cancelled': '#6C757D',   # Gray
            'declined': '#DC3545',    # Red
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display().upper()
        )
    
    @admin.display(description='Created')
    def created_time_ago(self, obj):
        """Show how long ago the transaction was created"""
        if not obj.timestamp:
            return '-'
        
        delta = timezone.now() - obj.timestamp
        
        if delta.days > 365:
            return "{} year(s) ago".format(delta.days // 365)
        elif delta.days > 30:
            return "{} month(s) ago".format(delta.days // 30)
        elif delta.days > 0:
            return "{} day(s) ago".format(delta.days)
        elif delta.seconds > 3600:
            return "{} hour(s) ago".format(delta.seconds // 3600)
        elif delta.seconds > 60:
            return "{} minute(s) ago".format(delta.seconds // 60)
        else:
            return "Just now"
    
    @admin.display(description='Sender Name')
    def sender_name_display(self, obj):
        """Display sender's full name"""
        return obj.sender_name
    
    @admin.display(description='Amount (Formatted)')
    def formatted_amount(self, obj):
        """Display formatted amount with currency symbol in detail view"""
        formatted_amount = '${:,.2f}'.format(obj.amount)
        return format_html(
            '<strong style="color: #28A745; font-size: 14px;">{}</strong>',
            formatted_amount
        )
    
    # Custom actions
    @admin.action(description='Mark selected as Completed')
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(
            request,
            '{} withdrawal(s) marked as completed.'.format(updated)
        )
    
    @admin.action(description='Mark selected as Cancelled')
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(
            request,
            '{} withdrawal(s) marked as cancelled.'.format(updated)
        )
    
    @admin.action(description='Mark selected as Declined')
    def mark_as_declined(self, request, queryset):
        updated = queryset.update(status='declined')
        self.message_user(
            request,
            '{} withdrawal(s) marked as declined.'.format(updated)
        )
    
    @admin.action(description='Mark selected as Pending')
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(
            request,
            '{} withdrawal(s) marked as pending.'.format(updated)
        )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    def save_model(self, request, obj, form, change):
        """Add custom logic when saving"""
        super().save_model(request, obj, form, change)
        
        # You can add notifications or logging here
        if change and 'status' in form.changed_data:
            # Log status change
            pass
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)  # Optional: add custom CSS
        }

@admin.register(PayPalWithdrawal)
class PayPalWithdrawalAdmin(BaseWithdrawalAdmin):
    list_display = [
        'timestamp',
        'user',
        'paypal_email',
        'get_amount_display',
        'get_status_display'
    ]
    search_fields = [
        'user__email',
        'user__username',
        'paypal_email'
    ]
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'timestamp')
        }),
        ('PayPal Details', {
            'fields': ('paypal_email',)
        }),
        ('Transaction Details', {
            'fields': ('amount', 'description', 'status')
        }),
    )

@admin.register(SkrillWithdrawal)
class SkrillWithdrawalAdmin(BaseWithdrawalAdmin):
    list_display = [
        'timestamp',
        'user',
        'skrill_email',
        'get_amount_display',
        'get_status_display'
    ]
    search_fields = [
        'user__email',
        'user__username',
        'skrill_email'
    ]
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'timestamp')
        }),
        ('Skrill Details', {
            'fields': ('skrill_email',)
        }),
        ('Transaction Details', {
            'fields': ('amount', 'description', 'status')
        }),
    )

@admin.register(RevolutWithdrawal)
class RevolutWithdrawalAdmin(BaseWithdrawalAdmin):
    list_display = [
        'timestamp',
        'user',
        'revolut_email',
        'get_amount_display',
        'get_status_display'
    ]
    search_fields = [
        'user__email',
        'user__username',
        'revolut_email'
    ]
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'timestamp')
        }),
        ('Revolut Details', {
            'fields': ('revolut_email',)
        }),
        ('Transaction Details', {
            'fields': ('amount', 'description', 'status')
        }),
    )

@admin.register(WiseWithdrawal)
class WiseWithdrawalAdmin(BaseWithdrawalAdmin):
    list_display = [
        'timestamp',
        'user',
        'wise_email',
        'get_amount_display',
        'get_status_display'
    ]
    search_fields = [
        'user__email',
        'user__username',
        'wise_email'
    ]
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'timestamp')
        }),
        ('Wise Details', {
            'fields': ('wise_email',)
        }),
        ('Transaction Details', {
            'fields': ('amount', 'description', 'status')
        }),
    )

# Add custom admin site configurations
admin.site.site_header = 'Banking System Administration'
admin.site.site_title = 'Banking System Admin'
admin.site.index_title = 'Banking System Management'
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'credit_facility', 'payment_tenure', 'amount', 'requested_at']
    list_filter = ['credit_facility', 'payment_tenure', 'requested_at']
    search_fields = ['user__email', 'amount', 'reason']
    readonly_fields = ['user', 'requested_at']
    
    fieldsets = (
        ('Loan Details', {
            'fields': ('user', 'credit_facility', 'payment_tenure', 'amount', 'reason')
        }),
        ('Additional Information', {
            'fields': ('requested_at',)
        })
    )

admin.site.register(LoanRequest, LoanRequestAdmin)



class PayBillsAdmin(admin.ModelAdmin):
    list_display = ['user', 'address1', 'city', 'state', 'zipcode', 'nickname', 'delivery_method', 'amount', 'get_date', 'status']
    list_filter = ['delivery_method', 'status']
    search_fields = ['user__username', 'address1', 'city', 'state', 'zipcode', 'nickname']
    ordering = ['-timestamp']
    actions = ['mark_as_paid', 'mark_as_cancelled']

    def get_date(self, obj):
        return f"{obj.year}-{obj.month:02d}-{obj.day:02d}"

    get_date.short_description = 'Date of Delivery'

    def mark_as_paid(self, request, queryset):
        rows_updated = queryset.update(status='completed')
        if rows_updated == 1:
            message_bit = "1 record was"
        else:
            message_bit = f"{rows_updated} records were"
        self.message_user(request, f"{message_bit} successfully marked as paid.")

    mark_as_paid.short_description = "Mark selected bills as paid"

    def mark_as_cancelled(self, request, queryset):
        rows_updated = queryset.update(status='cancelled')
        if rows_updated == 1:
            message_bit = "1 record was"
        else:
            message_bit = f"{rows_updated} records were"
        self.message_user(request, f"{message_bit} successfully marked as cancelled.")

    mark_as_cancelled.short_description = "Mark selected bills as cancelled"

admin.site.register(PayBills, PayBillsAdmin)

class CardDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_type', 'masked_card_number', 'expiry_month', 'expiry_year', 'card_owner', 'timestamp')
    search_fields = ('user__username', 'card_number', 'card_owner')
    list_filter = ('card_type', 'timestamp')

    def masked_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}"

    masked_card_number.short_description = 'Card Number'

admin.site.register(CardDetail, CardDetailAdmin)



class WithdrawalAdminForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # If editing an existing object
            if self.instance.approval_document:
                self.fields['approval_document'].help_text = format_html(
                    '<a href="{}" target="_blank" download>Download Approval Document</a>',
                    self.instance.approval_document.url if hasattr(self.instance.approval_document, 'url') else f"https://res.cloudinary.com/{self.instance.approval_document}"
                )
            if self.instance.fee_receipt:
                self.fields['fee_receipt'].help_text = format_html(
                    '<a href="{}" target="_blank" download>Download Fee Receipt</a>',
                    self.instance.fee_receipt.url if hasattr(self.instance.fee_receipt, 'url') else f"https://res.cloudinary.com/{self.instance.fee_receipt}"
                )



class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_email', 'amount', 'recipient_account', 'date', 'status', 'current_balance')
    list_filter = ('status', )
    search_fields = ('user__email', 'user__username')
    
    def client_name(self, obj):
        return obj.user.get_full_name()
    client_name.short_description = 'Client Name'
    
    def client_email(self, obj):
        return obj.user.email
    client_email.short_description = 'Client Email'
    
    def recipient_account(self, obj):
        return obj.target
    recipient_account.short_description = 'Recipient Account'
    
    def current_balance(self, obj):
        deposits = obj.user.deposits.aggregate(models.Sum('amount'))['amount__sum'] or 0
        withdrawals = obj.user.withdrawals.aggregate(models.Sum('amount'))['amount__sum'] or 0
        balance = deposits - withdrawals
        return balance
    current_balance.short_description = 'Current Balance'
    
admin.site.register(Withdrawal, WithdrawalAdmin)



class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'payment_method', 'status', 'date']
    list_filter = ['status', 'date']

    def save_model(self, request, obj, form, change):
        if change:
            original_obj = Payment.objects.get(pk=obj.pk)
            if original_obj.status != 'COMPLETE' and obj.status == 'COMPLETE':
                obj.update_balance()
            elif original_obj.status == 'COMPLETE' and obj.status != 'COMPLETE':
                obj.user.balance -= original_obj.amount
                obj.user.save()
        elif obj.status == 'COMPLETE':
            obj.update_balance()

        super().save_model(request, obj, form, change)


class CryptoWITHDRAWAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_method', 'amount', 'status', 'date')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'user__email')

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and form.cleaned_data['status'] == 'COMPLETE':
            obj.update_balance()
        obj.save()

admin.site.register(CryptoWITHDRAW, CryptoWITHDRAWAdmin)

class CRYPWALLETSAdmin(admin.ModelAdmin):
    list_display = ('bitcoin', 'ethereum')
    list_filter = ('bitcoin', 'ethereum')
    search_fields = ('bitcoin', 'ethereum')
admin.site.register(CRYPWALLETS, CRYPWALLETSAdmin)


@admin.register(MailSubscription)
class MailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed')
    search_fields = ('email',)
    list_filter = ('date_subscribed',)
    

admin.site.register(Payment, PaymentAdmin)
admin.site.add_action(export_as_csv, name='export_selected')

admin.site.register(SUPPORT)
