
from django.db import models
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from datetime import datetime, timedelta
from decimal import Decimal

User = settings.AUTH_USER_MODEL

class CardRequest(models.Model):
    CARD_TYPES = (
        ('China Union Pay', 'China Union Pay'),
        ('Dollar Card', 'Dollar Card'),
        ('Master Card', 'Master Card'),
        ('Visa Card', 'Visa Card'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    is_approved = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.card_type} - {self.is_approved}'

    class Meta:
        ordering = ('-date_created',)
    class Meta:
        verbose_name = "Card Request"
        verbose_name_plural = "Card Request"

class Card(models.Model):
    CARD_TYPES = (
        ('China Union Pay', 'China Union Pay'),
        ('Dollar Card', 'Dollar Card'),
        ('Master Card', 'Master Card'),
        ('Visa Card', 'Visa Card'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    card_number = models.CharField(max_length=16, unique=True)
    expire_date = models.DateField()
    cvv = models.CharField(max_length=3)
    date_created = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.fullname} - {self.card_type} - {self.card_number}'

    class Meta:
        ordering = ('-date_created',)


@receiver(post_save, sender=CardRequest)
def create_card(sender, instance, created, **kwargs):
    if created and instance.is_approved:
        card_number = str(random.randint(1000000000000000, 9999999999999999))
        expire_date = datetime.now() + timedelta(days=365)
        cvv = str(random.randint(100, 999))
        card = Card.objects.create(user=instance.user, card_type=instance.card_type, card_number=card_number,
                                   expire_date=expire_date, cvv=cvv)
        card.save()

# models.py

class CardDetails(models.Model):
    CARD_TYPES = [
        ('V', 'Visa'),
        ('M', 'Mastercard'),
        ('D', 'Discover'),
        ('A', 'American Express'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=255, choices=CARD_TYPES)
    card_number = models.SlugField(max_length=255)
    expiry_date = models.DateField()
    cvv = models.CharField(max_length=3)
    card_owner = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_type} **** **** **** {self.card_number[-4:]}"

    class Meta:
        verbose_name = "Card Credentials"
        verbose_name_plural = "Card Credentials"
