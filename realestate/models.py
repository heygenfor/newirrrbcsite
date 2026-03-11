from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField

User = get_user_model()


class PropertyType(models.Model):
    """Types of properties (House, Apartment, Villa, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Property Type"
        verbose_name_plural = "Property Types"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Property(models.Model):
    """Main property model"""
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
        ('pending', 'Pending'),
    )
    
    TRANSACTION_TYPE = (
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('both', 'Sale or Rent'),
    )
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE, related_name='properties')
    
    # Pricing
    price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    rent_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE, default='sale')
    
    # Location
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_map_embed = models.TextField(blank=True, null=True, help_text="Paste Google Maps iframe embed code")
    
    # Property Details
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    area_sqft = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    year_built = models.PositiveIntegerField(null=True, blank=True)
    garage = models.PositiveIntegerField(default=0)
    
    # Features
    has_pool = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    has_security = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    pet_friendly = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Agent/Contact
    agent_name = models.CharField(max_length=200, blank=True, null=True)
    agent_phone = models.CharField(max_length=30, blank=True, null=True)
    agent_email = models.EmailField(blank=True, null=True)
    
    # Metadata
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            self.slug = slugify(self.title) + '-' + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])
    
    @property
    def main_image(self):
        image = self.images.filter(is_main=True).first()
        if image:
            return image.image.url
        elif self.images.exists():
            return self.images.first().image.url
        return None


class PropertyImage(models.Model):
    """Property images"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image', folder='real_estate/properties/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Property Image"
        verbose_name_plural = "Property Images"
        ordering = ['order', '-is_main', '-uploaded_at']
    
    def __str__(self):
        return f"{self.property.title} - Image {self.order}"
    
    def save(self, *args, **kwargs):
        if self.is_main:
            # Ensure only one main image per property
            PropertyImage.objects.filter(property=self.property, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class PropertyApplication(models.Model):
    """User applications for properties"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_applications', null=True, blank=True)
    
    # Applicant Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    
    # Application Details
    message = models.TextField(help_text="Tell us why you're interested in this property")
    preferred_move_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Property Application"
        verbose_name_plural = "Property Applications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.property.title}"