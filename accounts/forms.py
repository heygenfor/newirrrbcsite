
import datetime
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import User, AccountDetails, UserAddress
from django.contrib.auth.forms import UserChangeForm





class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "contact_no",
        ]


class AccountDetailsForm(forms.ModelForm):
    DAY_CHOICES = [(str(day), str(day)) for day in range(1, 32)]
    MONTH_CHOICES = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]
    YEAR_CHOICES = [(str(year), str(year)) for year in range(1950, 2019)]

    day = forms.ChoiceField(choices=DAY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


    class Meta:
        model = AccountDetails
        fields = [
            'gender',
            'account_type',
            'account_currency',
            'occupation',
            'picture'
        ]
        widgets = {
            'picture': forms.ClearableFileInput(),
        }


    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.day = int(self.cleaned_data['day'])
        instance.month = int(self.cleaned_data['month'])
        instance.year = int(self.cleaned_data['year'])
        if commit:
            instance.save()
        return instance

class UserAddressForm(forms.ModelForm):
    COUNTRY_CHOICES = [
        ('', 'Select Country'),
        ('AF', 'Afghanistan'),
        ('AL', 'Albania'),
        ('AM', 'Armenia'),
        ('AO', 'Angola'),
        ('AR', 'Argentina'),
        ('AT', 'Austria'),
        ('AZ', 'Azerbaijan'),
        ('BA', 'Bosnia and Herzegovina'),
        ('BB', 'Barbados'),
        ('BD', 'Bangladesh'),
        ('BE', 'Belgium'),
        ('BF', 'Burkina Faso'),
        ('BG', 'Bulgaria'),
        ('BH', 'Bahrain'),
        ('BI', 'Burundi'),
        ('BJ', 'Benin'),
        ('BO', 'Bolivia'),
        ('BR', 'Brazil'),
        ('BS', 'Bahamas'),
        ('BT', 'Bhutan'),
        ('BW', 'Botswana'),
        ('BY', 'Belarus'),
        ('BZ', 'Belize'),
        ('CA', 'Canada'),
        ('CF', 'Central African Republic'),
        ('CH', 'Switzerland'),
        ('CL', 'Chile'),
        ('CM', 'Cameroon'),
        ('CN', 'China'),
        ('CO', 'Colombia'),
        ('CR', 'Costa Rica'),
        ('CU', 'Cuba'),
        ('CV', 'Cape Verde'),
        ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
        ('DE', 'Germany'),
        ('DJ', 'Djibouti'),
        ('DM', 'Dominica'),
        ('DO', 'Dominican Republic'),
        ('DZ', 'Algeria'),
        ('EC', 'Ecuador'),
        ('EE', 'Estonia'),
        ('EG', 'Egypt'),
        ('ER', 'Eritrea'),
        ('ES', 'Spain'),
        ('ET', 'Ethiopia'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('GA', 'Gabon'),
        ('GB', 'United Kingdom'),
        ('GD', 'Grenada'),
        ('GE', 'Georgia'),
        ('GH', 'Ghana'),
        ('GM', 'Gambia'),
        ('GN', 'Guinea'),
        ('GR', 'Greece'),
        ('GT', 'Guatemala'),
        ('GW', 'Guinea-Bissau'),
        ('GY', 'Guyana'),
        ('HN', 'Honduras'),
        ('HR', 'Croatia'),
        ('HT', 'Haiti'),
        ('HU', 'Hungary'),
        ('ID', 'Indonesia'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IN', 'India'),
        ('IQ', 'Iraq'),
        ('IR', 'Iran'),
        ('IS', 'Iceland'),
        ('IT', 'Italy'),
        ('JM', 'Jamaica'),
        ('JO', 'Jordan'),
        ('JP', 'Japan'),
        ('KE', 'Kenya'),
        ('KG', 'Kyrgyzstan'),
        ('KH', 'Cambodia'),
        ('KM', 'Comoros'),
        ('KN', 'Saint Kitts and Nevis'),
        ('KP', 'North Korea'),
        ('KR', 'South Korea'),
        ('KW', 'Kuwait'),
        ('KZ', 'Kazakhstan'),
        ('LA', 'Laos'),
        ('LB', 'Lebanon'),
        ('LC', 'Saint Lucia'),
        ('LI', 'Liechtenstein'),
        ('LK', 'Sri Lanka'),
        ('LR', 'Liberia'),
        ('LS', 'Lesotho'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('LV', 'Latvia'),
        ('LY', 'Libya'),
        ('MA', 'Morocco'),
        ('MD', 'Moldova'),
        ('ME', 'Montenegro'),
        ('MG', 'Madagascar'),
        ('MK', 'Macedonia'),
        ('ML', 'Mali'),
        ('MM', 'Myanmar'),
        ('MN', 'Mongolia'),
        ('MR', 'Mauritania'),
        ('MU', 'Mauritius'),
        ('MV', 'Maldives'),
        ('MW', 'Malawi'),
        ('MX', 'Mexico'),
        ('MY', 'Malaysia'),
        ('MZ', 'Mozambique'),
        ('NA', 'Namibia'),
        ('NE', 'Niger'),
        ('NG', 'Nigeria'),
        ('NI', 'Nicaragua'),
        ('NL', 'Netherlands'),
        ('NO', 'Norway'),
        ('NP', 'Nepal'),
        ('OM', 'Oman'),
        ('PA', 'Panama'),
        ('PE', 'Peru'),
        ('PG', 'Papua New Guinea'),
        ('PH', 'Philippines'),
        ('PK', 'Pakistan'),
        ('PL', 'Poland'),
        ('PS', 'Palestinian Territory'),
        ('PT', 'Portugal'),
        ('PY', 'Paraguay'),
        ('QA', 'Qatar'),
        ('RO', 'Romania'),
        ('RS', 'Serbia'),
        ('RU', 'Russia'),
        ('RW', 'Rwanda'),
        ('SA', 'Saudi Arabia'),
        ('SB', 'Solomon Islands'),
        ('SC', 'Seychelles'),
        ('SD', 'Sudan'),
        ('SE', 'Sweden'),
        ('SG', 'Singapore'),
        ('SI', 'Slovenia'),
        ('SK', 'Slovakia'),
        ('SL', 'Sierra Leone'),
        ('SM', 'San Marino'),
        ('SN', 'Senegal'),
        ('SO', 'Somalia'),
        ('SR', 'Suriname'),
        ('SS', 'South Sudan'),
        ('SV', 'El Salvador'),
        ('SY', 'Syria'),
        ('SZ', 'Swaziland'),
        ('TD', 'Chad'),
        ('TG', 'Togo'),
        ('TH', 'Thailand'),
        ('TJ', 'Tajikistan'),
        ('TL', 'East Timor'),
        ('TM', 'Turkmenistan'),
        ('TN', 'Tunisia'),
        ('TO', 'Tonga'),
        ('TR', 'Turkey'),
        ('TT', 'Trinidad and Tobago'),
        ('TW', 'Taiwan'),
        ('TZ', 'Tanzania'),
        ('UA', 'Ukraine'),
        ('UG', 'Uganda'),
        ('UK', 'United Kingdom'),
        ('US', 'United States'),
        ('UY', 'Uruguay'),
        ('UZ', 'Uzbekistan'),
        ('VC', 'Saint Vincent and the Grenadines'),
        ('VE', 'Venezuela'),
        ('VN', 'Vietnam'),
        ('VU', 'Vanuatu'),
        ('WS', 'Samoa'),
        ('YE', 'Yemen'),
        ('ZA', 'South Africa'),
        ('ZM', 'Zambia'),
        ('ZW', 'Zimbabwe')
    ]
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, label='Country', widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = UserAddress
        fields = [
            'postal_code',
            'country',
            'city',
            'state',
            'street_address',
            'religion',
        ]




class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
                'required': True,
            }
        )
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password',
                'required': True,
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['autocomplete'] = 'off'





class UserProfileEditForm(UserChangeForm):
    password = None  # Remove the password field from the form
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'contact_no']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_no': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AccountDetailsEditForm(forms.ModelForm):
    class Meta:
        model = AccountDetails
        fields = ['picture']
        widgets = {
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Your old password was entered incorrectly. Please enter it again.')
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data



