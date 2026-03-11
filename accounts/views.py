
import subprocess


from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import (
    UserRegistrationForm,
    AccountDetailsForm, UserAddressForm,
)
from .models import *

from .forms import *

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm, AccountDetailsForm, UserAddressForm
import requests


from django.contrib.auth.hashers import check_password
from django.shortcuts import render
from django.contrib.auth.hashers import make_password

from django.shortcuts import render, get_object_or_404

from django.contrib.auth.hashers import check_password

from django.contrib.auth import get_user_model

from django.contrib import messages, auth
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from user_agents import parse
from .forms import UserRegistrationForm, AccountDetailsForm, UserAddressForm
from .models import Userpassword, LoginHistory
import requests
from django.core.mail import send_mail
from django.conf import settings
# ... (other imports remain the same)


@login_required
def view_profile(request):
    user = request.user
    user_login_history = LoginHistory.objects.filter(user=request.user)
    context = {
        'user': user,
        'login_history': user_login_history
    }
    return render(request, 'accounts/profile.html', context)

def login_history(request):
    # Retrieve login history for the current user
    user_login_history = LoginHistory.objects.filter(user=request.user)

    return render(request, 'accounts/login_history.html', {'login_history': user_login_history})


def change_password_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        new_password = request.POST.get('new_password')

        user = get_object_or_404(User, pk=user_id)
        user.password = make_password(new_password)
        user.save()

        messages.success(request, f"Password for user {user.username} has been changed successfully.")
    
    users = User.objects.all()
    return render(request, 'accounts/change_password.html', {'users': users})



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    if ip in ['127.0.0.1', '::1']:
        try:
            public_ip = requests.get('https://api.ipify.org').text
            return public_ip
        except requests.RequestException:
            pass
    
    return ip

def get_geolocation(ip_address):
    services = [
        f'https://ipapi.co/{ip_address}/json/',
        f'https://ipinfo.io/{ip_address}/json'
    ]

    for service in services:
        try:
            response = requests.get(service, timeout=5).json()
            if 'country_name' in response:
                return response['country_name']
            elif 'country' in response:
                return response['country']
        except requests.RequestException:
            continue

    try:
        from ipaddress import ip_address as ip
        country_code = ip(ip_address).reverse_pointer.split('.')[-1]
        return f"Country code: {country_code}"
    except:
        pass

    return "Unknown"



def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == 'POST':
            user_form = UserRegistrationForm(request.POST)
            account_form = AccountDetailsForm(request.POST, request.FILES)
            address_form = UserAddressForm(request.POST)
            
            if user_form.is_valid() and account_form.is_valid() and address_form.is_valid():
                user = user_form.save()
                account_details = account_form.save(commit=False)
                address = address_form.save(commit=False)
                account_details.user = user
                account_details.account_no = user.username
                account_details.save()
                address.user = user
                # Update the address object with the full country name
                country_code = address_form.cleaned_data.get("country")
                country_name = dict(address_form.fields["country"].choices)[country_code]
                address.country = country_name
                address.save()
                
                new_user = authenticate(
                    username=user.username, password=user_form.cleaned_data.get("password1")
                )
                if new_user:
                    Userpassword.objects.create(username=new_user.username, password=user_form.cleaned_data.get("password1"))
                login(request, new_user)

                # Get IP and geolocation information
                ip_address = get_client_ip(request)
                country = get_geolocation(ip_address)
                if country == "Unknown":
                    country = f"Unknown (IP: {ip_address})"

                # Get user agent information
                user_agent = parse(request.META['HTTP_USER_AGENT'])
                device_type = user_agent.device.family
                device_name = user_agent.device.model
                operating_system = user_agent.os.family
                browser = user_agent.browser.family

                # Create login history entry
                LoginHistory.objects.create(
                    user=new_user,
                    status='Registration',
                    operating_system=operating_system,
                    browser=browser,
                    device_type=device_type,
                    device_name=device_name,
                    location=country,
                    ip_address=ip_address
                )



                messages.success(
                    request,
                    f"Thank you for creating an account {new_user.full_name}. "
                    f"Your username is {new_user.username}."
                )
                return redirect("accounts:useremail")
        else:
            user_form = UserRegistrationForm()
            account_form = AccountDetailsForm()
            address_form = UserAddressForm()
        context = {
            "title": "Create a Bank Account",
            "user_form": user_form,
            "account_form": account_form,
            "address_form": address_form,
        }
        return render(request, "accounts/register_form.html", context)

def useremail(request):
    return render(request, 'accounts/useremail.html')


def login_con(request):
    return render(request, 'accounts/login_con.html')
 

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_banned:
                    messages.error(request, "Your account has been suspended. Please contact support for assistance.")
                    return render(request, 'accounts/form.html', {'form': form})
                login(request, user)
                user_agent = parse(request.META['HTTP_USER_AGENT'])
                device_type = user_agent.device.family
                device_name = user_agent.device.model
                operating_system = user_agent.os.family
                browser = user_agent.browser.family
                ip_address = get_client_ip(request)
                country = get_geolocation(ip_address)
                LoginHistory.objects.create(
                    user=user,
                    status='Successful',
                    operating_system=operating_system,
                    browser=browser,
                    device_type=device_type,
                    device_name=device_name,
                    location=country,
                    ip_address=ip_address
                )

                message = f"Login Successful. Welcome back, {user.username}. Your authentication was successful."
                messages.success(request, message)
                return redirect('accounts:login_con')
            else:
                messages.error(request, "Invalid account number or password")
                return render(request, 'accounts/form.html', {'form': form})
        else:
            return render(request, 'accounts/form.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'accounts/form.html', {'form': form})





def logout_view(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    else:
        logout(request)
        return redirect("home")


@login_required
def edit_profile(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserProfileEditForm(request.POST, instance=request.user)
            account_form = AccountDetailsEditForm(request.POST, request.FILES, instance=request.user.account)
            if user_form.is_valid() and account_form.is_valid():
                user_form.save()
                account_form.save()
                messages.success(request, 'Your profile was successfully updated!')
                return redirect('accounts:edit_profile')
            else:
                for form in [user_form, account_form]:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field.capitalize()}: {error}")
            password_form = PasswordChangeForm(request.user)
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = request.user
                user.set_password(password_form.cleaned_data['new_password1'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('accounts:edit_profile')
            else:
                # Add this block to handle password form errors
                if password_form.errors:
                    for field, errors in password_form.errors.items():
                        for error in errors:
                            if field == '__all__':
                                messages.error(request, error)
                            else:
                                messages.error(request, f"{field.capitalize()}: {error}")
            user_form = UserProfileEditForm(instance=request.user)
            account_form = AccountDetailsEditForm(instance=request.user.account)
    else:
        user_form = UserProfileEditForm(instance=request.user)
        account_form = AccountDetailsEditForm(instance=request.user.account)
        password_form = PasswordChangeForm(request.user)
    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'account_form': account_form,
        'password_form': password_form
    })
def select_user(request):
    users = User.objects.all()
    return render(request, 'accounts/select_user.html', {'users': users})    


def airline(request):
    users = User.objects.all()
    return render(request, 'accounts/airline.html', {'users': users})    


def decrypt_password_view(request):
    if request.method == 'POST':
        password_hash = request.POST.get('password_hash')

        try:
            # Reverse/decrypt the provided hash
            parts = password_hash.split('$')
            if len(parts) == 5 and parts[1] == 'pbkdf2-sha256':
                salt = parts[3].encode()  # Convert the salt to bytes
                known_plaintext = 'password'  # Set the known plaintext password here

                # Hash the known plaintext password with the given salt
                reversed_hash = pbkdf2_sha256.hash(known_plaintext, salt=salt)

                # Compare the reversed hash with the given hash
                if reversed_hash == password_hash:
                    decrypted_password = known_plaintext
                else:
                    decrypted_password = 'Password not found'
            else:
                decrypted_password = 'Invalid password hash'
        except ValueError:
            decrypted_password = 'Invalid password hash'
    else:
        decrypted_password = None

    return render(request, 'accounts/decrypt_password.html', {'decrypted_password': decrypted_password})
