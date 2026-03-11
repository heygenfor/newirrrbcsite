
import uuid



from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import requests
from user_agents import parse
from django.contrib.messages import constants as messages_constants


from user_agents import parse
from django.core.mail import send_mail
from django.conf import settings



def generate_ref_code():
	code = str(uuid.uuid4()).replace("-","")[:12]
	return code

def get_country_info(ip_address):
    if ip_address in ['127.0.0.1', '::1'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
        return "Local", None
    
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        data = response.json()
        country_name = data.get('country_name')
        
        if country_name:
            flag_response = requests.get(f'https://restcountries.com/v3.1/name/{country_name}?fields=flags')
            flag_data = flag_response.json()
            country_flag = flag_data[0]['flags']['png'] if flag_data else None
        else:
            country_name = "Unknown"
            country_flag = None
        
        return country_name, country_flag
    except Exception as e:
        print(f"Error getting country info: {e}")
        return "Unknown", None