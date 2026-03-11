from django.contrib import admin
from django.utils.html import format_html
from .models import PropertyType, Property, PropertyImage, PropertyApplication


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'caption', 'is_main', 'order')
    readonly_fields = ('uploaded_at',)


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_count', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    def property_count(self, obj):
        return obj.properties.count()
    property_count.short_description = 'Number of Properties'


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'property_type', 
        'transaction_type',
        'price_display',
        'city', 
        'status', 
        'is_featured',
        'is_active',
        'views',
        'created_at'
    )
    list_filter = (
        'property_type', 
        'transaction_type',
        'status', 
        'is_featured', 
        'is_active',
        'city',
        'state',
        'created_at'
    )
    search_fields = ('title', 'description', 'address', 'city', 'state')
    inlines = [PropertyImageInline]
    
    def get_readonly_fields(self, request, obj=None):
        """Make slug readonly only when editing"""
        if obj:  # Editing an existing object
            return ('slug', 'views', 'created_at', 'updated_at', 'preview_map')
        return ('views', 'created_at', 'updated_at', 'preview_map')
    
    def get_fieldsets(self, request, obj=None):
        """Show slug only when editing"""
        if obj:  # Editing an existing object
            return (
                ('Basic Information', {
                    'fields': ('title', 'slug', 'description', 'property_type')
                }),
                ('Pricing & Transaction', {
                    'fields': ('transaction_type', 'price', 'rent_price')
                }),
                ('Location', {
                    'fields': (
                        'address', 'city', 'state', 'country', 'zip_code',
                        'latitude', 'longitude', 'google_map_embed', 'preview_map'
                    )
                }),
                ('Property Details', {
                    'fields': (
                        'bedrooms', 'bathrooms', 'area_sqft', 'year_built', 'garage'
                    )
                }),
                ('Features', {
                    'fields': (
                        'has_pool', 'has_garden', 'has_gym', 'has_security', 
                        'furnished', 'pet_friendly'
                    )
                }),
                ('Agent/Contact', {
                    'fields': ('agent_name', 'agent_phone', 'agent_email')
                }),
                ('Status & Visibility', {
                    'fields': ('status', 'is_featured', 'is_active')
                }),
                ('Metadata', {
                    'fields': ('views', 'created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        else:  # Adding a new object
            return (
                ('Basic Information', {
                    'fields': ('title', 'description', 'property_type')
                }),
                ('Pricing & Transaction', {
                    'fields': ('transaction_type', 'price', 'rent_price')
                }),
                ('Location', {
                    'fields': (
                        'address', 'city', 'state', 'country', 'zip_code',
                        'latitude', 'longitude', 'google_map_embed'
                    )
                }),
                ('Property Details', {
                    'fields': (
                        'bedrooms', 'bathrooms', 'area_sqft', 'year_built', 'garage'
                    )
                }),
                ('Features', {
                    'fields': (
                        'has_pool', 'has_garden', 'has_gym', 'has_security', 
                        'furnished', 'pet_friendly'
                    )
                }),
                ('Agent/Contact', {
                    'fields': ('agent_name', 'agent_phone', 'agent_email')
                }),
                ('Status & Visibility', {
                    'fields': ('status', 'is_featured', 'is_active')
                }),
            )
    
    def price_display(self, obj):
        if obj.transaction_type == 'sale':
            return f"${obj.price:,.2f}"
        elif obj.transaction_type == 'rent':
            return f"${obj.rent_price:,.2f}/month"
        else:
            return f"${obj.price:,.2f} / ${obj.rent_price:,.2f}/month"
    price_display.short_description = 'Price'
    
    def preview_map(self, obj):
        if obj.google_map_embed:
            return format_html(
                '<div style="max-width: 600px;">{}</div>',
                obj.google_map_embed
            )
        return "No map embed code provided"
    preview_map.short_description = 'Map Preview'
    
    actions = ['make_featured', 'remove_featured', 'mark_as_sold', 'mark_as_available']
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} properties marked as featured.')
    make_featured.short_description = 'Mark selected properties as featured'
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} properties removed from featured.')
    remove_featured.short_description = 'Remove featured status'
    
    def mark_as_sold(self, request, queryset):
        updated = queryset.update(status='sold')
        self.message_user(request, f'{updated} properties marked as sold.')
    mark_as_sold.short_description = 'Mark as sold'
    
    def mark_as_available(self, request, queryset):
        updated = queryset.update(status='available')
        self.message_user(request, f'{updated} properties marked as available.')
    mark_as_available.short_description = 'Mark as available'


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'caption', 'is_main', 'order', 'image_preview', 'uploaded_at')
    list_filter = ('is_main', 'uploaded_at')
    search_fields = ('property__title', 'caption')
    readonly_fields = ('image_preview', 'uploaded_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(PropertyApplication)
class PropertyApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'property',
        'email',
        'phone',
        'status',
        'preferred_move_date',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'preferred_move_date')
    search_fields = ('full_name', 'email', 'phone', 'property__title')
    readonly_fields = ('user', 'property', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Application Info', {
            'fields': ('property', 'user', 'status')
        }),
        ('Applicant Details', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Application Details', {
            'fields': ('message', 'preferred_move_date', 'budget')
        }),
        ('Admin Section', {
            'fields': ('admin_notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_applications', 'reject_applications', 'mark_reviewing']
    
    def approve_applications(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} applications approved.')
    approve_applications.short_description = 'Approve selected applications'
    
    def reject_applications(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} applications rejected.')
    reject_applications.short_description = 'Reject selected applications'
    
    def mark_reviewing(self, request, queryset):
        updated = queryset.update(status='reviewing')
        self.message_user(request, f'{updated} applications marked as under review.')
    mark_reviewing.short_description = 'Mark as under review'