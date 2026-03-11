from django import forms
from .models import PropertyApplication


class PropertyApplicationForm(forms.ModelForm):
    """Form for users to apply for properties"""
    
    class Meta:
        model = PropertyApplication
        fields = ['full_name', 'email', 'phone', 'message', 'preferred_move_date', 'budget']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us why you\'re interested in this property...',
                'rows': 5,
                'required': True
            }),
            'preferred_move_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your budget',
                'step': '0.01'
            }),
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'message': 'Why are you interested?',
            'preferred_move_date': 'Preferred Move-in Date',
            'budget': 'Your Budget ($)',
        }


class PropertySearchForm(forms.Form):
    """Form for searching/filtering properties"""
    
    TRANSACTION_CHOICES = [
        ('', 'All'),
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    ]
    
    STATUS_CHOICES = [
        ('', 'All'),
        ('available', 'Available'),
        ('pending', 'Pending'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, location, or description...'
        })
    )
    
    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '1000'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '1000'
        })
    )
    
    min_bedrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Bedrooms'
        })
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )