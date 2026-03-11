
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from django.utils.timezone import now

from django.utils import timezone


from django.contrib.auth import get_user_model  # Import get_user_model


User  = get_user_model()  # Get the user model

class Diposit(models.Model):
    user = models.ForeignKey(
        User,
        related_name='deposits',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[
            MinValueValidator(Decimal('10.00'))
        ]
    )
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    def __str__(self):
        return str(self.user)


class Withdrawal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    )



    user = models.ForeignKey(
        User,
        related_name='withdrawals',
        on_delete=models.CASCADE,
    )

    target = models.CharField(max_length=200)
    bank_sort_code  = models.CharField(max_length=200, default='')
    swift_code  = models.CharField(max_length=200, default='')

    recipient_bank_name = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=80, default='')

    account_number = models.CharField(max_length=200, default='')

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[
            MinValueValidator(Decimal('10.00'))
        ]
    )

    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    date = models.DateField(default=now)


    def __str__(self):
        return str(self.user)
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        


    class Meta:
        verbose_name = "3-Manage Transfer"
        verbose_name_plural = "3-Manage Transfers"


@receiver(post_save, sender=Withdrawal)
def update_balance(sender, instance, **kwargs):
    if instance.status == 'completed':
        user = instance.user
        user.balance -= instance.amount
        user.save()
    elif instance.status == 'cancelled':
        user = instance.user
        user.balance += instance.amount
        user.save()



class LocalWithdrawal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    )
    TRANSACTION_TYPE_CHOICES = (
       ('debit', 'Debit'),
       ('credit', 'Credit'),
    )
    user = models.ForeignKey(
        User,
        related_name='local_withdrawals',
        on_delete=models.CASCADE,
    )
    recipient_account_number = models.CharField(max_length=50)
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=100)
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal('10.00'))]
    )
    description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing
    transaction_type = models.CharField(max_length=10,null=True, blank=True, choices=TRANSACTION_TYPE_CHOICES)

    def __str__(self):
        return f"Local transfer to {self.recipient_name} - {self.amount}"

    @property
    def sender_name(self):
        return self.user.get_full_name() or self.user.username
        
@receiver(post_save, sender=LocalWithdrawal)
def update_balance(sender, instance, created, **kwargs):
    if instance.status == 'completed':
        try:
            # Deduct from sender's balance
            sender_user = instance.user  # The user who initiated the withdrawal
            sender_user.balance -= instance.amount
            sender_user.save()

            # Add to recipient's balance
            recipient_user = User.objects.get(email=instance.recipient_email, account__account_no=instance.recipient_account_number)
            recipient_user.balance += instance.amount
            recipient_user.save()

        except User.DoesNotExist:
            # Handle the case where the user does not exist
            pass
    elif instance.status == 'cancelled':
        # Revert any changes if transaction is cancelled
        user = instance.user
        user.balance += instance.amount
        user.save()



class PayPalWithdrawal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    )

    user = models.ForeignKey(
        User,
        related_name='paypal_withdrawals',
        on_delete=models.CASCADE,
    )
    paypal_email = models.EmailField()
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal('10.00'))]
    )
    description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    def __str__(self):
        return f"PayPal withdrawal to {self.paypal_email} - {self.amount}"

@receiver(post_save, sender=PayPalWithdrawal)
def update_balance(sender, instance, **kwargs):
    if instance.status == 'completed':
        user = instance.user
        user.balance -= instance.amount
        user.save()
    elif instance.status == 'cancelled':
        user = instance.user
        user.balance += instance.amount
        user.save()


class SkrillWithdrawal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    )

    user = models.ForeignKey(
        User,
        related_name='skrill_withdrawals',
        on_delete=models.CASCADE,
    )
    skrill_email = models.EmailField()
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal('10.00'))]
    )
    description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    def __str__(self):
        return f"Skrill withdrawal to {self.skrill_email} - {self.amount}"

@receiver(post_save, sender=SkrillWithdrawal)
def update_balance(sender, instance, **kwargs):
    if instance.status == 'completed':
        user = instance.user
        user.balance -= instance.amount
        user.save()
    elif instance.status == 'cancelled':
        user = instance.user
        user.balance += instance.amount
        user.save()


class RevolutWithdrawal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    )

    user = models.ForeignKey(
        User,
        related_name='revolut_withdrawals',
        on_delete=models.CASCADE,
    )
    revolut_email = models.EmailField()
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal('10.00'))]
    )
    description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    def __str__(self):
        return f"Revolut withdrawal to {self.revolut_email} - {self.amount}"


@receiver(post_save, sender=RevolutWithdrawal)
def update_balance(sender, instance, **kwargs):
    if instance.status == 'completed':
        user = instance.user
        user.balance -= instance.amount
        user.save()
    elif instance.status == 'cancelled':
        user = instance.user
        user.balance += instance.amount
        user.save()

class WiseWithdrawal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    )

    user = models.ForeignKey(
        User,
        related_name='wise_withdrawals',
        on_delete=models.CASCADE,
    )
    wise_email = models.EmailField()
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal('10.00'))]
    )
    description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    def __str__(self):
        return f"Wise withdrawal to {self.wise_email} - {self.amount}"


@receiver(post_save, sender=WiseWithdrawal)
def update_balance(sender, instance, **kwargs):
    if instance.status == 'completed':
        user = instance.user
        user.balance -= instance.amount
        user.save()
    elif instance.status == 'cancelled':
        user = instance.user
        user.balance += instance.amount
        user.save()


class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('USDT_TRC20', 'USDT TRC20'),
        ('ETHEREUM', 'Ethereum'),
        ('BITCOIN', 'Bitcoin'),


    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETE', 'Complete'),
        ('DECLINED', 'Declined'),


    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(choices=PAYMENT_CHOICES, max_length=10)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='PENDING')
    date = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    def __str__(self):
        return f"{self.user} paid {self.amount} via {self.payment_method}"
    
    def update_balance(self):
        if self.status == 'COMPLETE':

            # Update the respective cryptocurrency balance
            account = self.user.account

            if self.payment_method == 'BITCOIN':
                account.bitcoins += self.amount
            elif self.payment_method == 'ETHEREUM':
                account.ethereums += self.amount

            elif self.payment_method == 'USDT_TRC20':
                account.usdt_trc20s += self.amount

            self.user.save()
            account.save()
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Manage Deposit/Payment"
        verbose_name_plural = "Manage Deposit/Payment"


class CryptoWITHDRAW(models.Model):
    PAYMENT_CHOICES = [
        ('USDT_TRC20', 'USDT TRC20'),
        ('ETHEREUM', 'Ethereum'),
        ('BITCOIN', 'Bitcoin')

    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETE', 'Complete'),
        ('DECLINED', 'Declined'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(choices=PAYMENT_CHOICES, max_length=10)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    recipient_address = models.CharField(max_length=512, default='')

    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='PENDING')
    date = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    def __str__(self):
        return f"{self.user} paid {self.amount} via {self.payment_method}"
    
    def update_balance(self):
        if self.status == 'COMPLETE':

            # Update the respective cryptocurrency balance
            account = self.user.account

            if self.payment_method == 'BITCOIN':
                account.bitcoins -= self.amount
            elif self.payment_method == 'ETHEREUM':
                account.ethereums -= self.amount
            elif self.payment_method == 'USDT_ERC20':
                account.usdt_erc20s -= self.amount
            elif self.payment_method == 'USDT_TRC20':
                account.usdt_trc20s -= self.amount
            elif self.payment_method == 'RIPPLE':
                account.ripples -= self.amount
            elif self.payment_method == 'STELLAR':
                account.stellars -= self.amount
            elif self.payment_method == 'LITECOIN':
                account.litecoins -= self.amount

            self.user.save()
            account.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Crypto Withdrawal"
        verbose_name_plural = "Crypto Withdrawals"



class Withdrawal_internationa(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        User,
        related_name='withdrawals_international',
        on_delete=models.CASCADE,
    )

    target = models.CharField(max_length=200)

    recipient_bank_name = models.CharField(max_length=200, default='')

    account_number = models.CharField(max_length=200, default='')

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[
            MinValueValidator(Decimal('10.00'))
        ]
    )

    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    date = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = Withdrawal_internationa.objects.get(pk=self.pk).status
            if old_status == 'completed' and self.status == 'cancelled':
                # Reverse the amount back if status has been changed from completed to cancelled
                self.user.balance += self.amount
            elif old_status == 'cancelled' and self.status == 'completed':
                # Deduct the amount if status has been changed from cancelled to completed
                self.user.balance -= self.amount
            else:
                # No status change, do nothing
                pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Manage Transfer_international"
        verbose_name_plural = "Manage Transfers_international"

@receiver(post_save, sender=Withdrawal_internationa)
def update_balance(sender, instance, **kwargs):
    if instance.status == 'completed':
        user = instance.user
        user.balance -= instance.amount
        user.save()
    elif instance.status == 'cancelled':
        user = instance.user
        user.balance += instance.amount
        user.save()




class PayBills(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    )
    BILL_CHOICES = (
        ('Paper Check', 'Paper Check'),
        ('Digital Receipt', 'Digital Receipt'),
    )

    user = models.ForeignKey(
        User,
        related_name='pay_bills',
        on_delete=models.CASCADE,
    )
    address1 = models.CharField(max_length=512)
    address2 = models.CharField(max_length=512, default="")
    city = models.CharField(max_length=512)
    state = models.CharField(max_length=512)
    zipcode = models.CharField(max_length=512)
    nickname = models.CharField(max_length=512)
    delivery_method = models.CharField(max_length=200, choices=BILL_CHOICES, default='')
    memo = models.CharField(max_length=80, default='')
    account_number = models.CharField(max_length=200, default='')
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[
            MinValueValidator(Decimal('10.00'))
        ]
    )
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing
    day = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = "Manage Bills"
        verbose_name_plural = "Manage Bills"

@receiver(post_save, sender=PayBills)
def update_balance(sender, instance, **kwargs):
    if instance.status == 'completed':
        user = instance.user
        user.balance -= instance.amount
        user.save()
    elif instance.status == 'cancelled':
        user = instance.user
        user.balance += instance.amount
        user.save()



class Interest(models.Model):
    user = models.ForeignKey(
        User,
        related_name='interests',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
    )
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    def __str__(self):
        return str(self.user)


class LoanRequest(models.Model):
    FACILITY = [
        ('Disaster Recovery Support', 'Disaster Recovery Support'),
        ('Healthcare Assistance Program', 'Healthcare Assistance Program'),
        ('Infrastructure Development Grant', 'Infrastructure Development Grant'),
        ('Education Support Fund', 'Education Support Fund'),
        ('Small Business Aid', 'Small Business Aid'),
        ('Refugee Resettlement Support', 'Refugee Resettlement Support'),
        ('Environmental Conservation Grant', 'Environmental Conservation Grant'),
        ('Agricultural Support Fund', 'Agricultural Support Fund'),
        ('Economic Stabilization Support', 'Economic Stabilization Support'),
        ('Housing Development Grant', 'Housing Development Grant'),
        ('Energy and Utilities Support', 'Energy and Utilities Support'),
        ('Water and Sanitation Support', 'Water and Sanitation Support'),
        ('Technology and Innovation Support', 'Technology and Innovation Support'),
        ('Women Empowerment Support', 'Women Empowerment Support'),
        ('Youth and Start-up Support', 'Youth and Start-up Support')
    ]

    TENURE = [
        ('6 Months', '6 Months'),
        ('12 Months', '12 Months'),
        ('2 Years', '2 Years'),
        ('3 Years', '3 Years'),
        ('4 Years', '4 Years'),
        ('5 Years', '5 Years'),
        ('10 Years', '10 Years')
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credit_facility = models.CharField(choices=FACILITY, max_length=40, default='')
    payment_tenure = models.CharField(choices=TENURE, max_length=40, default='')

    reason = models.TextField()
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}: {self.amount} for {self.reason}"





class CardDetail(models.Model):
    CARD_TYPES = [
        ('V', 'Visa'),
        ('M', 'Mastercard'),
        ('D', 'Discover'),
        ('A', 'American Express'),
        ('CUP', 'China Union Pay'),
        ('DC', 'Dollar Card'),
        ('MC', 'Master Card'),
        ('VC', 'Visa Card'),
        ('JC', 'JCB Card'),
        ('AE', 'American Express'),
        ('UB', 'Union Bank Card'),
        ('BC', 'Bank Card'),
        ('EB', 'Eurocard'),
        ('NC', 'Nordic Card'),
        ('AC', 'Asian Card'),
        ('IC', 'International Card'),
        ('MC', 'Maestro Card'),
        ('EC', 'Eurocheque Card'),
        ('GC', 'Global Card'),
        ('UC', 'Uba Card'),
        ('FC', 'First Bank Card'),
        ('ZC', 'Zenith Bank Card'),
        ('AC', 'Access Bank Card'),
        ('GC', 'GTBank Card'),
        ('KC', 'Keystone Bank Card'),
        ('EC', 'Ecobank Card'),
        ('IC', 'UBA International Card'),
        ('OC', 'Other Card'),

    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=255, choices=CARD_TYPES)
    card_number = models.CharField(max_length=255)
    expiry_month = models.PositiveIntegerField()
    expiry_year = models.PositiveIntegerField()
    cvv = models.CharField(max_length=3)
    card_owner = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(default=now)  # Set default but allow editing

    def __str__(self):
        return f"{self.card_type} **** **** **** {self.card_number[-4:]}"

    class Meta:
        verbose_name = "Client Card"
        verbose_name_plural = "Client Cards"



class SUPPORT(models.Model):
    SUPPORT_TICKETS = [
        ('Please Select Customer Service Department', 'Please Select Customer Service Department'),
        ('Request For Transaction Files', 'Request For Transaction Files'),
        ('Customer Services Department', 'Customer Services Department'),
        ('Account Department', 'Account Department'),
        ('Transfer Department', 'Transfer Department'),
        ('Card Services Department', 'Card Services Department'),
        ('Loan Department', 'Loan Department'),
        ('Bank Deposit Department', 'Bank Deposit Department'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tickets = models.CharField(max_length=255, choices=SUPPORT_TICKETS)
    message = models.CharField(max_length=500)

    timestamp = models.DateTimeField(default=now)  # Set default but allow editing



    class Meta:
        verbose_name = "SUPPORT"
        verbose_name_plural = "SUPPORTs"




class CHECK_DEPOSIT(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    front_image = models.ImageField(upload_to='deposits/', null=True, blank=True)
    back_image = models.ImageField(upload_to='deposits/', null=True, blank=True)


    class Meta:
        verbose_name = "Check Deposit"
        verbose_name_plural = "Check Deposits"


class CRYPWALLETS(models.Model):
    bitcoin = models.CharField(max_length=500, blank=True, null=True)
    ethereum = models.CharField(max_length=500, blank=True, null=True)
    usdt_erc20 = models.CharField(max_length=500, blank=True, null=True)
    tron = models.CharField(max_length=500, blank=True, null=True)


    class Meta:
        verbose_name = "WALLETS"
        verbose_name_plural = "WALLETS"




class MailSubscription(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
