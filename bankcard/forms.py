from django import forms
from .models import *

class CardRequestForm(forms.ModelForm):
    CARD_TYPES = (
        ('China Union Pay', 'China Union Pay'),
        ('Dollar Card', 'Dollar Card'),
        ('Master Card', 'Master Card'),
        ('Visa Card', 'Visa Card'),
    )

    card_type = forms.ChoiceField(choices=CARD_TYPES, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, user=None, *args, **kwargs):
        super(CardRequestForm, self).__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = CardRequest
        fields = ['card_type']

# forms.py

class CardDetailsForm(forms.ModelForm):
    class Meta:
        model = CardDetails
        fields = ['card_type', 'card_number', 'expiry_date', 'cvv']
        widgets = {
            'card_type': forms.Select(attrs={'class': 'form-control'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.TextInput(attrs={'class': 'form-control'}),
            'cvv': forms.TextInput(attrs={'class': 'form-control'}),
        }

