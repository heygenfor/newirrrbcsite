from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CardRequest, Card
from datetime import datetime, timedelta
import random
import string
from .forms import CardRequestForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from datetime import datetime, timedelta
import random
import string
from accounts.models import User

import datetime

def generate_expiry_date():
    # Generate expiry date for the card, which is the current date plus 3 years
    current_date = datetime.datetime.now()
    expiry_date = current_date + datetime.timedelta(days=3*365)
    return expiry_date

def generate_cvv():
    return random.randint(100, 999)


@login_required
def card_request(request):
    if request.method == 'POST':
        form = CardRequestForm(request.user, request.POST)  # Pass user parameter to the form
        if form.is_valid():
            card_request = form.save(commit=False)
            card_request.user = request.user
            card_request.save()
            messages.success(request, 'Your card request has been submitted.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CardRequestForm(user=request.user)  # Pass user parameter to the form
    return render(request, 'bankcard/card_request.html', {'form': form})



@login_required
def card_approval(request, card_request_id):
    card_request = get_object_or_404(CardRequest, id=card_request_id)
    if request.user != card_request.user:
        messages.error(request, 'You are not authorized to approve this card request.')
        return redirect('home')
    if card_request.is_approved:
        messages.warning(request, 'This card request has already been approved.')
        return redirect('home')
    card_type = card_request.card_type
    card_number = generate_card_number()
    expire_date = datetime.now() + timedelta(days=365)
    cvv = ''.join(random.choices(string.digits, k=3))
    card = Card.objects.create(user=request.user, card_type=card_type, card_number=card_number, expire_date=expire_date, cvv=cvv)
    card_request.is_approved = True
    card_request.save()
    messages.success(request, 'Card request approved.')
    return render(request, 'bankcard/card_details.html', {'card': card})


def generate_card_number():
    while True:
        card_number = ''.join(random.choices(string.digits, k=16))
        if not Card.objects.filter(card_number=card_number).exists():
            return card_number



@login_required
def user_cards(request):
    card_details = CardDetails.objects.filter(user=request.user).order_by('timestamp')
    return render(request, 'bankcard/view_card.html', {'card_details': card_details})



@login_required
def cards_types(request):
    return render(request, 'bankcard/card_type.html')


@login_required
def approve_select_user(request):
    users = User.objects.all()
    if request.method == 'POST':
        user_email = request.POST.get('user')
        user = get_object_or_404(User, email=user_email)
        card_type = request.POST.get('card_type')
        card_number = generate_card_number()
        expiry_date = generate_expiry_date()
        cvv = generate_cvv()
        card_owner = f"{user.first_name} {user.last_name}"
        card_details = CardDetails(user=user, card_type=card_type, card_number=card_number,
                                   expiry_date=expiry_date, cvv=cvv, card_owner=card_owner)
        card_details.save()

        return redirect('bankcard:approve_select_user')
    else:
        form = CardRequestForm(user=request.user)
    return render(request, 'bankcard/approve_select_user.html', {'users': users, 'form': form})
