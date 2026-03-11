
from django import forms

from django import forms
from .models import *
from datetime import date

class SupportForm(forms.ModelForm):
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

    tickets = forms.ChoiceField(choices=SUPPORT_TICKETS, widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Department'}))

    class Meta:
        model = SUPPORT
        fields = ['tickets', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control'}),
        }


class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ['credit_facility', 'payment_tenure', 'reason', 'amount']
        widgets = {
            'credit_facility': forms.Select(attrs={'class': 'form-control'}),
            'payment_tenure': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        

class CardDetailsForm(forms.ModelForm):
    card_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Card Number'}),
        error_messages={'required': 'Please enter your card number.'}
    )
    expiry_month = forms.ChoiceField(
        choices=[('', 'Month')] + [(str(month), str(month)) for month in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please select the expiry month of your card.'}
    )

    expiry_year = forms.ChoiceField(
        choices=[('', 'Year')] + [(str(year), str(year)) for year in range(date.today().year, date.today().year + 10)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please select the expiry year of your card.'}
    )

    cvv = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CVV'}),
        error_messages={'required': 'Please enter the CVV code.'}
    )
    card_owner = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Card Owner'}),
        error_messages={'required': 'Please enter the card owner name.'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['card_type'].widget.attrs.update({'class': 'form-control custom-select card-type-select'})

    def as_card_type_field(self):
        card_type_field = self['card_type']
        card_type_field.field.widget = forms.Select(attrs={'class': 'form-control custom-select'})
        card_type_field.field.widget.choices = [('', 'Select Card Type')] + list(card_type_field.field.choices)[1:]
        return card_type_field

    class Meta:
        model = CardDetail
        fields = ('card_type', 'card_number', 'expiry_month', 'expiry_year', 'cvv', 'card_owner')


class CheckDepositForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'})
    )
    front_image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        required=False
    )
    back_image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        required=False
    )

    class Meta:
        model = CHECK_DEPOSIT
        fields = ['amount', 'front_image', 'back_image']

class PayBillsForm(forms.ModelForm):
    DAY_CHOICES = [(str(day), str(day)) for day in range(1, 32)]
    MONTH_CHOICES = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]
    YEAR_CHOICES = [(str(year), str(year)) for year in range(2022, 2032)]

    day = forms.ChoiceField(choices=DAY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = PayBills
        fields = ['address1', 'address2', 'city', 'state', 'zipcode', 'nickname', 'delivery_method', 'memo', 'account_number', 'amount']

        widgets = {
            'address1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address 1'}),
            'address2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address 2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter state'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter zipcode'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Payee name'}),
            'delivery_method': forms.Select(attrs={'class': 'form-control'}),
            'memo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter memo'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter account number', 'pattern': '[0-9]*'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount', 'step': '0.01', 'min': '10.00'}),
        }

        labels = {
            'address1': 'Address 1',
            'address2': 'Address 2',
            'city': 'City',
            'state': 'State',
            'zipcode': 'Zipcode',
            'nickname': 'Nickname',
            'delivery_method': 'Delivery Method',
            'memo': 'Memo (Max 80 characters)',
            'account_number': 'Account Number',
            'amount': 'Amount',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.day = int(self.cleaned_data['day'])
        instance.month = int(self.cleaned_data['month'])
        instance.year = int(self.cleaned_data['year'])
        if commit:
            instance.save()
        return instance


class DepositForm(forms.ModelForm):
    class Meta:
        model = Diposit
        fields = ["amount"]




class WithdrawalForm(forms.ModelForm):


    recipient_bank_name = forms.CharField(
        label='Recipient Bank Name',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Withdrawal
        fields = [
            'target',
            'bank_sort_code',
            'swift_code',
            'recipient_bank_name',
            'description',
            'account_number',
            'amount',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs.update({'class': 'form-control'})



# forms.py
class LocalWithdrawalForm(forms.ModelForm):
    class Meta:
        model = LocalWithdrawal
        fields = ['recipient_account_number', 'recipient_email', 'recipient_name', 'amount', 'description']
        widgets = {
            'recipient_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'recipient_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PayPalWithdrawalForm(forms.ModelForm):
    class Meta:
        model = PayPalWithdrawal
        fields = ['paypal_email', 'amount', 'description']
        widgets = {
            'paypal_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SkrillWithdrawalForm(forms.ModelForm):
    class Meta:
        model = SkrillWithdrawal
        fields = ['skrill_email', 'amount', 'description']
        widgets = {
            'skrill_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RevolutWithdrawalForm(forms.ModelForm):
    class Meta:
        model = RevolutWithdrawal
        fields = ['revolut_email', 'amount', 'description']
        widgets = {
            'revolut_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class WiseWithdrawalForm(forms.ModelForm):
    class Meta:
        model = WiseWithdrawal
        fields = ['wise_email', 'amount', 'description']
        widgets = {
            'wise_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }




class WithdrawalInternationalForm(forms.ModelForm):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, required=True)
    target_account_number = forms.CharField(max_length=20, required=True)
    target_bank_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Withdrawal_internationa
        fields = ["amount", "target_account_number", "target_bank_name"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(WithdrawalInternationalForm, self).__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if self.user.account.balance < amount:
            raise forms.ValidationError(
                'You cannot withdraw more than your available balance.'
            )

        return amount

    def clean_target_account_number(self):
        target_account_number = self.cleaned_data['target_account_number'].strip()
        return target_account_number

    def clean_target_bank_name(self):
        target_bank_name = self.cleaned_data['target_bank_name'].strip()
        return target_bank_name



class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'amount']



class CryptoWITHDRAWForm(forms.ModelForm):
    class Meta:
        model = CryptoWITHDRAW
        fields = ['payment_method', 'amount', 'recipient_address']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'recipient_address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def has_error(self, field_name):
        return self[field_name].errors

    def get_error(self, field_name):
        return self[field_name].errors.as_text()


class Client_USDTerc20Form(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    address = forms.CharField()



class Client_Trc20_form(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    address = forms.CharField()

class Client_Bitcoin_form(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    address = forms.CharField()


class Client_Ethereum_form(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    address = forms.CharField()
