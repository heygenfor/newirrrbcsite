from django.contrib import admin
from .models import CardRequest, Card, CardDetails
from bankingsystem.admin_actions import export_as_csv


class CardRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_type', 'is_approved', 'date_created')

    def client_name(self, obj):
        return obj.user.fullname
    client_name.short_description = 'Client Name'

    def client_email(self, obj):
        return obj.user.email
    client_email.short_description = 'Client Email'


class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_type', 'card_number', 'expire_date', 'cvv', 'date_created')

    def client_name(self, obj):
        return obj.user.fullname
    client_name.short_description = 'Client Name'

    def client_email(self, obj):
        return obj.user.email
    client_email.short_description = 'Client Email'



@admin.register(CardDetails)
class CardDetailsAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_email', 'get_card_type_display', 'expiry_date', 'cvv', 'timestamp')
    
    def client_name(self, obj):
        return obj.user.full_name
    
    def client_email(self, obj):
        return obj.user.email
    
    client_name.short_description = 'Client Name'
    client_email.short_description = 'Client Email'

admin.site.register(CardRequest, CardRequestAdmin)
admin.site.register(Card, CardAdmin)
admin.site.add_action(export_as_csv, name='export_selected')
