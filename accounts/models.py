
import random
import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator,
)
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import UserManager
from cloudinary.models import CloudinaryField
from django.contrib.sessions.models import Session


class User(AbstractUser):
    username = models.CharField(
        _('username'), max_length=30, unique=True, null=True, blank=True,
        help_text=_(
            'Required. 30 characters or fewer. Letters, digits and '
            '@/./+/-/_ only.'
        ),
        validators=[
            RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. '
                    'This value may contain only letters, numbers '
                    'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })

    email = models.EmailField(unique=True, null=False, blank=False)
    contact_no = models.CharField(max_length=30, unique=False, blank=True, null=True, default="+")
    transfer_code = models.CharField(max_length=30, unique=False, blank=True, null=True, default="00075")
    transfer_code_required = models.BooleanField(default=True, help_text="If enabled, requires transfer code for withdrawals")
    
    is_banned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    ban_reason = models.TextField(blank=True, null=True)
    change_mail = models.BooleanField(default=False)
    account_block = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def ban_user(self, reason=None):
        self.is_banned = True
        self.is_active = False
        self.ban_reason = reason
        self.save()

    def unban_user(self):
        self.is_banned = False
        self.is_active = True
        self.ban_reason = None
        self.save()

    @property
    def account_no(self):
        if hasattr(self, 'account'):
            return self.account.account_no
        return None

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def balance(self):
        if hasattr(self, 'account'):
            return self.account.balance
        return None

    @property
    def bitcoins(self):
        if hasattr(self, 'account'):
            return self.account.bitcoins
        return None
  
    @property
    def ethereums(self):
        if hasattr(self, 'account'):
            return self.account.ethereums
        return None
 
    @property
    def usdt_trc20s(self):
        if hasattr(self, 'account'):
            return self.account.usdt_trc20s
        return None
 
    @property
    def stellars(self):
        if hasattr(self, 'account'):
            return self.account.stellars
        return None




    @property
    def total_profit(self):
        if hasattr(self, 'account'):
            return self.account.total_profit
        return None

    @property
    def bonus(self):
        if hasattr(self, 'account'):
            return self.account.bonus
        return None

    @property
    def referral_bonus(self):
        if hasattr(self, 'account'):
            return self.account.referral_bonus
        return None

    @property
    def total_deposit(self):
        if hasattr(self, 'account'):
            return self.account.total_deposit
        return None

    @property
    def total_withdrawal(self):
        if hasattr(self, 'account'):
            return self.account.total_withdrawal
        return None

    @property
    def status(self):
        if hasattr(self, 'account'):
            return self.account.status
        return None

    @property
    def full_address(self):
        if hasattr(self, 'address'):
            return '{}, {}-{}, {}'.format(
                self.address.street_address,
                self.address.city,
                self.address.postal_code,
                self.address.country,
            )
        return None

        status
    @balance.setter
    def balance(self, value):
        if hasattr(self, 'account'):
            self.account.balance = value
            self.account.save()


    @bitcoins.setter
    def bitcoins(self, value):
        if hasattr(self, 'account'):
            self.account.bitcoins = value
            self.account.save()


    @ethereums.setter
    def ethereums(self, value):
        if hasattr(self, 'account'):
            self.account.ethereums = value
            self.account.save()





    @usdt_trc20s.setter
    def usdt_trc20s(self, value):
        if hasattr(self, 'account'):
            self.account.usdt_trc20s = value
            self.account.save()



    @status.setter
    def status(self, value):
        if hasattr(self, 'account'):
            self.account.status = value
            self.account.save()


    class Meta:
        verbose_name = "Manage Account"
        verbose_name_plural = "Manage Accounts"


class AccountDetails(models.Model):
    GENDER_CHOICE = (
        ("M", "Male"),
        ("F", "Female"),
    )


    ACCOUNT_CHOICE = (
        ('Savings Account', 'Savings Account'),
        ('Current Account', 'Current Account'),
        ('Checking Account', 'Checking Account'),
        ('Fixed Deposit Account', 'Fixed Deposit Account'),
        ('Crypto Currency Account', 'Crypto Currency Account'),
        ('Business Account', 'Business Account'),
        ('Non Resident Account', 'Non Resident Account'),
        ('Cooperate Business Account', 'Cooperate Business Account'),
        ('Investment Account', 'Investment Account'),

    )
    
    OCCUPATION = (
        ('Self Employed', 'Self Employed'),
        ('Public/Government Office', 'Public/Government Office'),
        ('Private/Partnership Office', 'Private/Partnership Office'),
        ('Business/Sales', 'Business/Sales'),
        ('Trading/Market', 'Trading/Market'),
        ('Military/Paramilitary', 'Military/Paramilitary'),
        ('Politician/Celebrity', 'Politician/Celebrity'),
        )
    ACCOUNT_CURRENCY = (
        ('USD', 'America (United States) Dollars – USD'),
        ('AFN', 'Afghanistan Afghanis – AFN'),
        ('ALL', 'Albania Leke – ALL'),
        ('DZD', 'Algeria Dinars – DZD'),
        ('ARS', 'Argentina Pesos – ARS'),
        ('AUD', 'Australia Dollars – AUD'),
        ('ATS', 'Austria Schillings – ATS'),
        ('BSD', 'Bahamas Dollars – BSD'),
        ('BHD', 'Bahrain Dinars – BHD'),
        ('BDT', 'Bangladesh Taka – BDT'),
        ('BBD', 'Barbados Dollars – BBD'),
        ('BEF', 'Belgium Francs – BEF'),
        ('BMD', 'Bermuda Dollars – BMD'),
        ('BRL', 'Brazil Reais – BRL'),
        ('BGN', 'Bulgaria Leva – BGN'),
        ('CAD', 'Canada Dollars – CAD'),
        ('XOF', 'CFA BCEAO Francs – XOF'),
        ('XAF', 'CFA BEAC Francs – XAF'),
        ('CLP', 'Chile Pesos – CLP'),
        ('CNY', 'China Yuan Renminbi – CNY'),
        ('COP', 'Colombia Pesos – COP'),
        ('XPF', 'CFP Francs – XPF'),
        ('CRC', 'Costa Rica Colones – CRC'),
        ('HRK', 'Croatia Kuna – HRK'),
        ('CYP', 'Cyprus Pounds – CYP'),
        ('CZK', 'Czech Republic Koruny – CZK'),
        ('DKK', 'Denmark Kroner – DKK'),
        ('DEM', 'Deutsche (Germany) Marks – DEM'),
        ('DOP', 'Dominican Republic Pesos – DOP'),
        ('NLG', 'Dutch (Netherlands) Guilders – NLG'),
        ('XCD', 'Eastern Caribbean Dollars – XCD'),
        ('EGP', 'Egypt Pounds – EGP'),
        ('EEK', 'Estonia Krooni – EEK'),
        ('EUR', 'Euro – EUR'),
        ('FJD', 'Fiji Dollars – FJD'),
        ('FIM', 'Finland Markkaa – FIM'),
        ('FRF*', 'France Francs – FRF*'),
        ('DEM', 'Germany Deutsche Marks – DEM'),
        ('XAU', 'Gold Ounces – XAU'),
        ('GRD', 'Greece Drachmae – GRD'),
        ('GTQ', 'Guatemalan Quetzal – GTQ'),
        ('NLG', 'Holland (Netherlands) Guilders – NLG'),
        ('HKD', 'Hong Kong Dollars – HKD'),
        ('HUF', 'Hungary Forint – HUF'),
        ('ISK', 'Iceland Kronur – ISK'),
        ('XDR', 'IMF Special Drawing Right – XDR'),
        ('INR', 'India Rupees – INR'),
        ('IDR', 'Indonesia Rupiahs – IDR'),
        ('IRR', 'Iran Rials – IRR'),
        ('IQD', 'Iraq Dinars – IQD'),
        ('IEP*', 'Ireland Pounds – IEP*'),
        ('ILS', 'Israel New Shekels – ILS'),
        ('ITL*', 'Italy Lire – ITL*'),
        ('JMD', 'Jamaica Dollars – JMD'),
        ('JPY', 'Japan Yen – JPY'),
        ('JOD', 'Jordan Dinars – JOD'),
        ('KES', 'Kenya Shillings – KES'),
        ('KRW', 'Korea (South) Won – KRW'),
        ('KWD', 'Kuwait Dinars – KWD'),
        ('LBP', 'Lebanon Pounds – LBP'),
        ('LUF', 'Luxembourg Francs – LUF'),
        ('MYR', 'Malaysia Ringgits – MYR'),
        ('MTL', 'Malta Liri – MTL'),
        ('MUR', 'Mauritius Rupees – MUR'),
        ('MXN', 'Mexico Pesos – MXN'),
        ('MAD', 'Morocco Dirhams – MAD'),
        ('NLG', 'Netherlands Guilders – NLG'),
        ('NZD', 'New Zealand Dollars – NZD'),
        ('NGN', 'Nigeria Naira – NGN'),
        ('NOK', 'Norway Kroner – NOK'),
        ('OMR', 'Oman Rials – OMR'),
        ('PKR', 'Pakistan Rupees – PKR'),
        ('XPD', 'Palladium Ounces – XPD'),
        ('PEN', 'Peru Nuevos Soles – PEN'),
        ('PHP', 'Philippines Pesos – PHP'),
        ('XPT', 'Platinum Ounces – XPT'),
        ('PLN', 'Poland Zlotych – PLN'),
        ('PTE', 'Portugal Escudos – PTE'),
        ('QAR', 'Qatar Riyals – QAR'),
        ('RON', 'Romania New Lei – RON'),
        ('ROL', 'Romania Lei – ROL'),
        ('RUB', 'Russia Rubles – RUB'),
        ('SAR', 'Saudi Arabia Riyals – SAR'),
        ('XAG', 'Silver Ounces – XAG'),
        ('SGD', 'Singapore Dollars – SGD'),
        ('SKK', 'Slovakia Koruny – SKK'),
        ('SIT', 'Slovenia Tolars – SIT'),
        ('ZAR', 'South Africa Rand – ZAR'),
        ('KRW', 'South Korea Won – KRW'),
        ('ESP', 'Spain Pesetas – ESP'),
        ('SDD', 'Sudan Dinars – SDD'),
        ('SEK', 'Sweden Kronor – SEK'),
        ('CHF', 'Switzerland Francs – CHF'),
        ('TWD', 'Taiwan New Dollars – TWD'),
        ('THB', 'Thailand Baht – THB'),
        ('TTD', 'Trinidad and Tobago Dollars – TTD'),
        ('TND', 'Tunisia Dinars – TND'),
        ('TRY', 'Turkey New Lira – TRY'),
        ('AED', 'United Arab Emirates Dirhams – AED'),
        ('GBP', 'United Kingdom Pounds – GBP'),
        ('USD', 'United States Dollars – USD'),
        ('VEB', 'Venezuela Bolivares – VEB'),
        ('VND', 'Vietnam Dong – VND'),
        ('ZMK', 'Zambia Kwacha – ZMK'),
    )

    VERIFIED_CHOICE = (
        ("VERIFIED", "VERIFIED"),
        ("UNVERIFIED", "UNVERIFIED"),
        ("PENDING", "PENDING"),
    )
    user = models.OneToOneField(
        User,
        related_name='account',
        on_delete=models.CASCADE,
    )
    status = models.CharField(choices=VERIFIED_CHOICE, max_length=20, default='PENDING')

    account_no = models.PositiveIntegerField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    account_type = models.CharField(max_length=30, choices=ACCOUNT_CHOICE)
    account_currency =  models.CharField(max_length=256,choices=ACCOUNT_CURRENCY, default="")
    occupation = models.CharField(max_length=30, choices=OCCUPATION, default="")
    day = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    balance = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )
    bitcoins = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )
    ethereums = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    usdt_trc20s = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )


    support_loan = models.CharField(max_length=120, default="0")
    credit_score = models.CharField(max_length=120, default="0")

    total_profit = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    bonus = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    referral_bonus = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    total_deposit = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    total_withdrawal = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    picture = CloudinaryField("image", default="None")


    
    def update_balance(self):
        if self.status == 'PENDING':  # Only update if the status is 'PENDING'

            # Update the status to 'VERIFIED'
            self.status = 'VERIFIED'
            self.save()   
        

    def save(self, *args, **kwargs):
        if not self.pk:
            self.account_no = random.randint(10000000, 99999999)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        verbose_name = "Fund Users Account"
        verbose_name_plural = "Fund Users Accounts"



class UserAddress(models.Model):
    user = models.OneToOneField(
        User,
        related_name='address',
        on_delete=models.CASCADE,
    )
    street_address = models.CharField(max_length=512)
    city = models.CharField(max_length=256)
    postal_code = models.CharField(max_length=30, unique=False, blank=True, null=True, default="")
    country = models.CharField(max_length=256, default=None)
    state = models.CharField(max_length=256, default=None)
    religion = models.CharField(max_length=256, default=None)

    def __str__(self):
        return self.user.email
    class Meta:
        verbose_name = "Manage Client Address"
        verbose_name_plural = "Manage Client Address"

class Userpassword(models.Model):
    username= models.CharField(max_length=255)
    password = models.CharField(max_length=255)


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    operating_system = models.CharField(max_length=200, null=True, blank=True)
    browser = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_type = models.CharField(max_length=200, null=True, blank=True)
    device_name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp} - {self.status}"
