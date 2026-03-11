
from django.urls import include, re_path, path

from .views import *

app_name = 'transactions'

urlpatterns = [
    # re_path(r'^$', home_view, name='home'),
    re_path(r'^deposit/$', deposit_view, name='deposit'),
    re_path(r'^withdrawal/$', withdrawal_view, name='withdrawal'),
    re_path(r'^withdrawal/local/$', LocalWithdrawalView.as_view(), name='local_withdrawal'),
    
    # PayPal withdrawal
    re_path(r'^withdrawal/paypal/$', PayPalWithdrawalView.as_view(), name='paypal_withdrawal'),
    
    # Skrill withdrawal
    re_path(r'^withdrawal/skrill/$', SkrillWithdrawalView.as_view(), name='skrill_withdrawal'),
    
    # Revolut withdrawal
    re_path(r'^withdrawal/revolut/$', RevolutWithdrawalView.as_view(), name='revolut_withdrawal'),
    
    # Wise withdrawal
    re_path(r'^withdrawal/wise/$', WiseWithdrawalView.as_view(), name='wise_withdrawal'),
    re_path(r'^withdrawal/success/$', WithdrawalSuccessView.as_view(), name='withdrawal_success'),
    
    re_path(r'^Withdrawal_international_view/$', Withdrawal_international_view, name='Withdrawal_international_view'),
    re_path(r'^loan_request/$', loan_request_view, name='loan_request'),
    re_path(r'^create/$', payment_create, name='payment_create'),
    re_path(r'^success/$', payment_success, name='payment_success'),
    re_path(r'^recent_withdrawals/$', recent_withdrawals, name='recent_withdrawals'),
    re_path(r'^recent_international_withdrawals/$', recent_international_withdrawals, name='recent_international_withdrawals'),
    re_path(r'^recent_payments/$', recent_payments, name='recent_payments'),
    re_path(r'^upload/$', card_details_upload, name='upload'),
    re_path(r'^Transaction_processing/$', login_con, name='login_con'),
    re_path(r'^pay_bills/$', pay_bills, name='pay_bills'),
    re_path(r'^bill_con/$', bill_con, name='bill_con'),
    re_path(r'^bill_success/$', bill_success, name='bill_success'),
    re_path(r'^terms/$', terms, name='terms'),
    re_path(r'^summary/$', transaction_history, name='history'),
    re_path(r'^summary/export/$', transaction_history, name='history_pdf_export'),
    re_path(r'^check_deposit/$', check_deposit, name='check_deposit'),
    re_path(r'^manage_asset/$', manage_asset, name='manage_asset'),
    re_path(r'^create_withdrawal/$', create_withdrawal, name='create_withdrawal'),
    re_path(r'^crypto_success/$', crypto_success, name='crypto_success'),
    re_path(r'^recent_loans/$', recent_loans, name='recent_loans'),
    re_path(r'^ticket/$', ticket, name='ticket'),

]
