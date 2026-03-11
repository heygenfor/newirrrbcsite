
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from .models import *
from .forms import *
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse

@login_required
def ticket(request):
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            support_ticket = form.save(commit=False)
            support_ticket.user = request.user
            support_ticket.save()
            messages.success(request, 'Your support ticket has been submitted successfully.')
            return redirect('transactions:ticket')  # Redirect to the same page (ticket view)
    else:
        form = SupportForm()

    user = request.user
    ticketlist = SUPPORT.objects.filter(user=user).order_by('-id')    
    context = {
        'form': form,
        'ticketlist': ticketlist
    }
    return render(request, 'transactions/ticket.html', context)


@login_required
def loan_request_view(request):
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            loan_request = form.save(commit=False)
            loan_request.user = request.user
            loan_request.save()
            messages.success(request, 'Thank you! Your UN grant request has been received. Notification will be sent within 24 hours.')
            return redirect('home')
    else:
        form = LoanRequestForm()
    context = {
        'title': 'Loan Request',
        'form': form,
    }
    return render(request, 'transactions/loan_request.html', context)

@login_required
def recent_loans(request):
    recent_loans = LoanRequest.objects.order_by()[:10]
    context = {'recent_loans': recent_loans}
    return render(request, 'transactions/loans.html', context)

@login_required()
def deposit_view(request):
    form = DepositForm(request.POST or None)

    if form.is_valid():
        deposit = form.save(commit=False)
        deposit.user = request.user
        deposit.save()
        # adds users deposit to balance.
        deposit.user.account.balance += deposit.amount
        deposit.user.account.save()
        messages.success(request, 'You Have Deposited {} $.'
                         .format(deposit.amount))
        return redirect("home")

    context = {
        "title": "Deposit",
        "form": form
    }
    return render(request, "transactions/form.html", context)


from django.db.models import F

import cloudinary
import cloudinary.uploader


@login_required
def withdrawal_view(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user

            withdrawal_amount = withdrawal.amount
            account_balance = withdrawal.user.account.balance

            if withdrawal_amount > account_balance:
                form.add_error('amount', 'Insufficient balance. You cannot withdraw more than your account balance.')
            else:
                withdrawal.status = 'pending'
                withdrawal.save()
                return redirect('transactions:login_con')
    else:
        form = WithdrawalForm()
    
    context = {
        'form': form,
        'transfer_code_required': request.user.transfer_code_required
    }
    return render(request, 'transactions/form.html', context)


# views.py

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import LocalWithdrawal
from .forms import LocalWithdrawalForm

User  = get_user_model()  # Get the user model

class LocalWithdrawalView(LoginRequiredMixin, CreateView):
    model = LocalWithdrawal
    form_class = LocalWithdrawalForm
    template_name = 'transactions/new_paym/local_withdrawal.html'

    def get_success_url(self):
        return reverse_lazy('transactions:withdrawal_success') + f'?type=local&id={self.object.id}'

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Check if the user exists with the provided email and account number
        try:
            user = User.objects.get(email=form.cleaned_data['recipient_email'], account__account_no=form.cleaned_data['recipient_account_number'])
        except User.DoesNotExist:
            messages.error(self.request, "No user found with the provided email and account number.")
            return self.form_invalid(form)

        if form.instance.amount > self.request.user.balance:
            messages.error(self.request, "Insufficient funds")
            return self.form_invalid(form)

        messages.success(self.request, "Local withdrawal request submitted successfully")
        return super().form_valid(form)


class PayPalWithdrawalView(LoginRequiredMixin, CreateView):
    model = PayPalWithdrawal
    form_class = PayPalWithdrawalForm
    template_name = 'transactions/new_paym/paypal_withdrawal.html'
    def get_success_url(self):
        return reverse_lazy('transactions:withdrawal_success') + f'?type=paypal&id={self.object.id}'

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.instance.amount > self.request.user.balance:
            messages.error(self.request, "Insufficient funds")
            return self.form_invalid(form)
        messages.success(self.request, "PayPal withdrawal request submitted successfully")
        return super().form_valid(form)

class SkrillWithdrawalView(LoginRequiredMixin, CreateView):
    model = SkrillWithdrawal
    form_class = SkrillWithdrawalForm
    template_name = 'transactions/new_paym/skrill_withdrawal.html'
    def get_success_url(self):
        return reverse_lazy('transactions:withdrawal_success') + f'?type=skrill&id={self.object.id}'

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.instance.amount > self.request.user.balance:
            messages.error(self.request, "Insufficient funds")
            return self.form_invalid(form)
        messages.success(self.request, "Skrill withdrawal request submitted successfully")
        return super().form_valid(form)

class RevolutWithdrawalView(LoginRequiredMixin, CreateView):
    model = SkrillWithdrawal
    form_class = RevolutWithdrawalForm
    template_name = 'transactions/new_paym/revo_withdrawal.html'
    def get_success_url(self):
        return reverse_lazy('transactions:withdrawal_success') + f'?type=revolut&id={self.object.id}'

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.instance.amount > self.request.user.balance:
            messages.error(self.request, "Insufficient funds")
            return self.form_invalid(form)
        messages.success(self.request, "Revolut withdrawal request submitted successfully")
        return super().form_valid(form)


class WiseWithdrawalView(LoginRequiredMixin, CreateView):
    model = SkrillWithdrawal
    form_class = WiseWithdrawalForm
    template_name = 'transactions/new_paym/wise_withdrawal.html'
    def get_success_url(self):
        return reverse_lazy('transactions:withdrawal_success') + f'?type=wise&id={self.object.id}'
    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.instance.amount > self.request.user.balance:
            messages.error(self.request, "Insufficient funds")
            return self.form_invalid(form)
        messages.success(self.request, "Wise withdrawal request submitted successfully")
        return super().form_valid(form)



from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    LocalWithdrawal, 
    PayPalWithdrawal, 
    SkrillWithdrawal,
    RevolutWithdrawal,
    WiseWithdrawal
)

class WithdrawalSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/withdrawal_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        withdrawal_type = self.request.GET.get('type', '')
        withdrawal_id = self.request.GET.get('id', '')
        
        # Get the transaction details based on withdrawal type
        transaction = None
        if withdrawal_type == 'local':
            transaction = LocalWithdrawal.objects.get(id=withdrawal_id)
        elif withdrawal_type == 'paypal':
            transaction = PayPalWithdrawal.objects.get(id=withdrawal_id)
        elif withdrawal_type == 'skrill':
            transaction = SkrillWithdrawal.objects.get(id=withdrawal_id)
        elif withdrawal_type == 'revolut':
            transaction = RevolutWithdrawal.objects.get(id=withdrawal_id)
        elif withdrawal_type == 'wise':
            transaction = WiseWithdrawal.objects.get(id=withdrawal_id)

        withdrawal_info = {
            'local': {
                'title': 'Local Bank Transfer',
                'message': 'Your local bank transfer request has been submitted successfully.',
                'icon': 'fa-bank'
            },
            'paypal': {
                'title': 'PayPal Withdrawal',
                'message': 'Your PayPal withdrawal request has been submitted successfully.',
                'icon': 'fa-paypal'
            },
            'skrill': {
                'title': 'Skrill Withdrawal',
                'message': 'Your Skrill withdrawal request has been submitted successfully.',
                'icon': 'fa-wallet'
            },
            'revolut': {
                'title': 'Revolut Withdrawal',
                'message': 'Your Revolut withdrawal request has been submitted successfully.',
                'icon': 'fa-exchange'
            },
            'wise': {
                'title': 'Wise Transfer',
                'message': 'Your Wise transfer request has been submitted successfully.',
                'icon': 'fa-globe'
            }
        }

        context.update({
            'withdrawal_info': withdrawal_info.get(withdrawal_type, {}),
            'withdrawal_type': withdrawal_type,
            'transaction': transaction,
            'user': self.request.user
        })
        return context


@login_required
def login_con(request):
    return render(request, 'transactions/login_con.html')

def terms(request):
    return render(request, 'transactions/terms.html')
    
@login_required
def pay_bills(request):
    if request.method == 'POST':
        form = PayBillsForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.user = request.user

            # Check if the bill amount is greater than the account balance
            bill_amount = bill.amount
            account_balance = bill.user.account.balance

            if bill_amount > account_balance:
                # Insufficient balance, form submission is halted
                form.add_error('amount', 'Insufficient balance. You cannot pay more than your account balance.')
            else:
                # Deduct the bill amount from the account balance using F() expression
                #bill.user.account.balance = F('balance') - bill_amount
                bill.user.account.save()

                bill.save()

                # Add a success message with details
                message = f"Thank you, {request.user.username}! Your bill payment for {bill.nickname} has been successfully processed."
                messages.success(request, message)

                return redirect('transactions:bill_con')  # Replace 'bill_con' with the appropriate URL name for the success page
    else:
        form = PayBillsForm()

    context = {
        'form': form,
    }
    return render(request, 'transactions/pay_bills.html', context)


@login_required
def bill_success(request):
    payment = PayBills.objects.filter(user=request.user).order_by('-id').first()
    return render(request, 'transactions/bill_success.html', {'payment': payment})

@login_required
def bill_con(request):
    return render(request, 'transactions/bill_con.html')

@login_required
def manage_asset(request):
    if not request.user.is_authenticated:
        return render(request, "core/index.html", {})
    
    user = request.user
    cryptowithdrawals = CryptoWITHDRAW.objects.filter(user=user).order_by('-id')
    cryptowithdra = Payment.objects.filter(user=user).order_by('-id')

    context = {
        "user": user,
        "cryptowithdrawals": cryptowithdrawals,
        "cryptowithdra": cryptowithdra,
        "title": "ROYAL BANK"
    }

    return render(request, 'transactions/manage.html', context)



@login_required
def Withdrawal_international_view(request):
    if request.method == 'POST':
        form = WithdrawalInternationalForm(request.POST, user=request.user)

        if form.is_valid():
            withdrawal_international = form.save(commit=False)
            withdrawal_international.user = request.user
            withdrawal_international.target = form.cleaned_data['target_account_number']
            withdrawal_international.recipient_bank_name = form.cleaned_data['target_bank_name']
            withdrawal_international.account_number = form.cleaned_data['target_account_number']
            withdrawal_international.save()

            messages.success(request, 'Your international withdrawal request has been submitted.')
            return redirect('inter_confirm')

    else:
        form = WithdrawalInternationalForm(user=request.user)

    return render(request, 'transactions/inter_form.html', {'form': form})


@login_required
def card_details_upload(request):
    if request.method == 'POST':
        form = CardDetailsForm(request.POST)
        if form.is_valid():
            card_details = form.save(commit=False)
            card_details.user = request.user
            card_details.save()
            messages.success(request, 'Card details uploaded successfully.')  # Add success message
            return redirect('home')
    else:
        form = CardDetailsForm()

    context = {'form': form}
    return render(request, 'transactions/card_upload.html', context)




@login_required
def payment_create(request):
    bank_transfer_methods = BankTransfer.objects.all()  # Fetch all bank transfer objects
    wallets_instance = CRYPWALLETS.objects.first()  # Fetch crypto wallet addresses
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.save()
            # Handle wallet address for crypto
            if payment.payment_method in ['BITCOIN', 'ETHEREUM', 'USDT_TRC20']:
                crypto_wallet = {
                    'BITCOIN': wallets_instance.bitcoin,
                    'ETHEREUM': wallets_instance.ethereum,
                    'USDT_TRC20': wallets_instance.tron,
                }.get(payment.payment_method, '')
                return render(request, 'transactions/payment_success.html', {
                    'payment': payment,
                    'crypto_wallet': crypto_wallet,
                })
            return redirect('transactions:payment_success')
        else:
            # Add error handling for invalid form
            error_messages = form.errors.as_json()  # Get form errors in JSON format
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")  # Display each error to the user

    else:
        form = PaymentForm()
    
    return render(request, 'transactions/payment_form.html', {
        'form': form,
        'bank_transfer_methods': bank_transfer_methods,
        'wallets_instance': wallets_instance,
    })


@login_required
def payment_success(request):
    payment = Payment.objects.filter(user=request.user).order_by('-id').first()
    return render(request, 'transactions/payment_success.html', {'payment': payment})

def create_withdrawal(request):
    if request.method == 'POST':
        form = CryptoWITHDRAWForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user

            # Check if the withdrawal amount exceeds the user's balance for the chosen cryptocurrency
            account = withdrawal.user.account

            if withdrawal.payment_method == 'BITCOIN' and withdrawal.amount > account.bitcoins:
                form.add_error('amount', 'Insufficient Bitcoin balance.')
            elif withdrawal.payment_method == 'ETHEREUM' and withdrawal.amount > account.ethereums:
                form.add_error('amount', 'Insufficient Ethereum balance.')
            elif withdrawal.payment_method == 'USDT_ERC20' and withdrawal.amount > account.usdt_erc20s:
                form.add_error('amount', 'Insufficient USDT ERC20 balance.')
            elif withdrawal.payment_method == 'USDT_TRC20' and withdrawal.amount > account.usdt_trc20s:
                form.add_error('amount', 'Insufficient USDT TRC20 balance.')
            elif withdrawal.payment_method == 'RIPPLE' and withdrawal.amount > account.ripples:
                form.add_error('amount', 'Insufficient Ripple balance.')
            elif withdrawal.payment_method == 'STELLAR' and withdrawal.amount > account.stellars:
                form.add_error('amount', 'Insufficient Stellar balance.')
            elif withdrawal.payment_method == 'LITECOIN' and withdrawal.amount > account.litecoins:
                form.add_error('amount', 'Insufficient Litecoin balance.')

            if not form.errors:
                withdrawal.save()
                withdrawal.update_balance()
                return redirect('transactions:crypto_success')  # Replace with your success URL
    else:
        form = CryptoWITHDRAWForm()
    
    return render(request, 'transactions/withdrawal_form.html', {'form': form})


@login_required
def crypto_success(request):
    payment = CryptoWITHDRAW.objects.filter(user=request.user).order_by('-id').first()
    return render(request, 'transactions/withdraw_success.html', {'payment': payment})

def recent_withdrawals(request):
    recent_withdrawals = Withdrawal.objects.order_by('-date', '-timestamp')[:10]
    context = {'recent_withdrawals': recent_withdrawals}
    return render(request, 'transactions/withdraw.html', context)



def recent_international_withdrawals(request):
    recent_international_withdrawals = Withdrawal_internationa.objects.order_by('-date', '-timestamp')[:10]
    context = {'recent_international_withdrawals': recent_international_withdrawals}
    return render(request, 'transactions/withdraw_international.html', context)



def recent_payments(request):
    recent_payments = Payment.objects.order_by('-date', '-timestamp')[:10]
    context = {'recent_payments': recent_payments}
    return render(request, 'transactions/payment.html', context)


from io import BytesIO
import os
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph

@login_required
def transaction_history(request):
    user = request.user
    deposit_history = Diposit.objects.filter(user=user).order_by('-timestamp')
    withdrawal_history = Withdrawal.objects.filter(user=user).order_by('-timestamp')
    payment_history = Payment.objects.filter(user=user).order_by('-date')
    crypto_history = CryptoWITHDRAW.objects.filter(user=user).order_by('-date')
    pay_bills = PayBills.objects.filter(user=user).order_by('-timestamp')
    local_withdrawals_sent = LocalWithdrawal.objects.filter(user=user).order_by('-timestamp')
    local_withdrawals_received = LocalWithdrawal.objects.filter(recipient_email=user.email).order_by('-timestamp')
    
    # Add new withdrawal types
    paypal_withdrawals = PayPalWithdrawal.objects.filter(user=user).order_by('-timestamp')
    skrill_withdrawals = SkrillWithdrawal.objects.filter(user=user).order_by('-timestamp')
    revolut_withdrawals = RevolutWithdrawal.objects.filter(user=user).order_by('-timestamp')
    wise_withdrawals = WiseWithdrawal.objects.filter(user=user).order_by('-timestamp')

    context = {
        'deposit_history': deposit_history,
        'withdrawal_history': withdrawal_history,
        'payment_history': payment_history,
        'crypto_history': crypto_history,
        'pay_bills': pay_bills,
        'local_withdrawals_sent': local_withdrawals_sent,
        'local_withdrawals_received': local_withdrawals_received,
        'paypal_withdrawals': paypal_withdrawals,
        'skrill_withdrawals': skrill_withdrawals,
        'revolut_withdrawals': revolut_withdrawals,
        'wise_withdrawals': wise_withdrawals,
    }

    if 'export' in request.GET and request.GET['export'] == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="transaction_history.pdf"'

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []

        # Define the path to the logo and add the logo
        image_path = os.path.join(os.path.abspath(os.path.join(settings.BASE_DIR, 'static')), 'dig73.png')
        logo = Image(image_path, width=120, height=60)
        elements.append(logo)
        elements.append(Spacer(1, 12))

        # Add PDF Title
        styles = getSampleStyleSheet()
        title = Paragraph(f"Transaction History for {user.username}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))

        # Table headers with enhanced formatting
        data = [
            ["Ref", "Type", "Scope", "Amount", "Date", "Time", "Method/Details", "Status"],
        ]

        # Date and time formatting function
        def format_datetime(dt):
            return dt.strftime('%d %B %Y'), dt.strftime('%I:%M %p')

        # Deposit History
        for deposit in deposit_history:
            date_str, time_str = format_datetime(deposit.timestamp)
            ref = f"D-{user.id}-{deposit.pk}-{str(user.account_no)[-4:]}"
            data.append([ref, "Deposit", "Transfer", f"{user.account.account_currency} {deposit.amount}", date_str, time_str, deposit.payment_method, deposit.status])

        # Withdrawal History
        for withdrawal in withdrawal_history:
            date_str, time_str = format_datetime(withdrawal.timestamp)
            ref = f"W-{user.id}-{withdrawal.pk}-{str(user.account_no)[-4:]}"
            data.append([ref, "Debit", "Transfer", f"{user.account.account_currency} {withdrawal.amount}", date_str, time_str, withdrawal.recipient_bank_name, withdrawal.status])

        # Payment History (with crypto/gift card/bank transfer details)
        for payment in payment_history:
            date_str, time_str = format_datetime(payment.timestamp)
            ref = f"P-{user.id}-{payment.pk}-{str(user.account_no)[-4:]}"
            if payment.payment_method == 'BANK_TRANSFER':
                details = f"{payment.bank_transfer.method} - {payment.bank_transfer.name_tag}"
            elif payment.payment_method == 'GIFTCARD':
                details = f"Gift Card: {payment.giftcard_type}, Code: {payment.giftcard_code}"
            else:
                # Handle crypto payments with wallets info
                details = f"Crypto: {payment.payment_method}"
            data.append([ref, "Payment", "Transfer", f"{user.account.account_currency} {payment.amount}", date_str, time_str, details, payment.status])

        # Pay Bills History
        for payment in pay_bills:
            date_str, time_str = format_datetime(payment.timestamp)
            ref = f"PB-{user.id}-{payment.pk}-{str(user.account_no)[-4:]}"
            data.append([ref, "Pay Bill", payment.delivery_method, f"{user.account.account_currency} {payment.amount}", date_str, time_str, payment.nickname, payment.status])

        # Add local withdrawals sent to PDF
        for transfer in local_withdrawals_sent:
            date_str, time_str = format_datetime(transfer.timestamp)
            ref = f"LW-{user.id}-{transfer.pk}-{str(user.account_no)[-4:]}"
            data.append([
                ref,
                transfer.transaction_type or "Debit",
                "Local Transfer",
                f"{user.account.account_currency} {transfer.amount}",
                date_str,
                time_str,
                f"To: {transfer.recipient_name}",
                transfer.status
            ])

        # Add local withdrawals received to PDF
        for transfer in local_withdrawals_received:
            date_str, time_str = format_datetime(transfer.timestamp)
            ref = f"LW-{transfer.user.id}-{transfer.pk}-{str(user.account_no)[-4:]}"
            data.append([
                ref,
                transfer.transaction_type or "Credit",
                "Local Transfer",
                f"{user.account.account_currency} {transfer.amount}",
                date_str,
                time_str,
                f"From: {transfer.sender_name}",
                transfer.status
            ])

        # PayPal Withdrawals
        for withdrawal in paypal_withdrawals:
            date_str, time_str = format_datetime(withdrawal.timestamp)
            ref = f"PP-{user.id}-{withdrawal.pk}-{str(user.account_no)[-4:]}"
            data.append([
                ref,
                "Debit",
                "PayPal Withdrawal",
                f"{user.account.account_currency} {withdrawal.amount}",
                date_str,
                time_str,
                f"PayPal: {withdrawal.paypal_email}",
                withdrawal.status
            ])

        # Skrill Withdrawals
        for withdrawal in skrill_withdrawals:
            date_str, time_str = format_datetime(withdrawal.timestamp)
            ref = f"SK-{user.id}-{withdrawal.pk}-{str(user.account_no)[-4:]}"
            data.append([
                ref,
                "Debit",
                "Skrill Withdrawal",
                f"{user.account.account_currency} {withdrawal.amount}",
                date_str,
                time_str,
                f"Skrill: {withdrawal.skrill_email}",
                withdrawal.status
            ])

        # Revolut Withdrawals
        for withdrawal in revolut_withdrawals:
            date_str, time_str = format_datetime(withdrawal.timestamp)
            ref = f"RV-{user.id}-{withdrawal.pk}-{str(user.account_no)[-4:]}"
            data.append([
                ref,
                "Debit",
                "Revolut Withdrawal",
                f"{user.account.account_currency} {withdrawal.amount}",
                date_str,
                time_str,
                f"Revolut: {withdrawal.revolut_email}",
                withdrawal.status
            ])

        # Wise Withdrawals
        for withdrawal in wise_withdrawals:
            date_str, time_str = format_datetime(withdrawal.timestamp)
            ref = f"WS-{user.id}-{withdrawal.pk}-{str(user.account_no)[-4:]}"
            data.append([
                ref,
                "Debit",
                "Wise Withdrawal",
                f"{user.account.account_currency} {withdrawal.amount}",
                date_str,
                time_str,
                f"Wise: {withdrawal.wise_email}",
                withdrawal.status
            ])

        # Create the table with enhanced styling
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
            ('BACKGROUND', (0, 1), (-1, -1), '#F1F1F1'),
            ('TEXTCOLOR', (0, 1), (-1, -1), '#000000'),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['#FFFFFF', '#F9F9F9']),
            ('GRID', (0, 0), (-1, -1), 1, '#DDDDDD'),
        ]))

        elements.append(table)
        doc.build(elements)

        # Get the value of the BytesIO buffer and add it to the response
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response

    return render(request, 'transactions/history.html', context)




@csrf_exempt  # Only for demonstration purposes; consider CSRF protection
def subscribe(request):
    response_data = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                validate_email(email)
                subscription, created = MailSubscription.objects.get_or_create(email=email)
                response_data['message'] = 'Thank you! Your submission has been received!' if created else 'You are already subscribed to our newsletter!'
            except ValidationError:
                response_data['message'] = 'Invalid email address. Please enter a valid email.'
            except Exception as e:
                response_data['message'] = 'An error occurred: ' + str(e)
        return JsonResponse(response_data)
    return JsonResponse({'message': 'Invalid request. Please use POST method to subscribe.'})

def check_deposit(request):
    if request.method == 'POST':
        form = CheckDepositForm(request.POST, request.FILES)
        if form.is_valid():
            check_deposit = form.save(commit=False)
            check_deposit.user = request.user
            check_deposit.save()
            amount = check_deposit.amount

            messages.success(request, f"Check deposit of ${amount:.2f} successfully submitted! You will receive a notification about the transaction details.")
            return redirect('home')
    else:
        form = CheckDepositForm()
    return render(request, 'transactions/check_deposit.html', {'form': form})

