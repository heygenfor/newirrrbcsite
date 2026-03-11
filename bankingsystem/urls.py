"""bankingsystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.static import static
from django.contrib import admin

from core.views import *
from transactions.views import *

urlpatterns = [
    # admin
    re_path('adman', include('admin_soft.urls')),
    re_path(r'^admin/', admin.site.urls),
    # Accounts
    re_path(r'^accounts/', include('accounts.urls', namespace='accounts')),
    re_path(r'^bankcard/', include('bankcard.urls', namespace='bankcard')),
    re_path(r'^properties/', include('realestate.urls')),
    # core
    re_path(r'^$', home, name='home'),
    re_path(r'welcome$', index, name='index'),
    re_path(r'^about/$', about, name='about'),
    re_path(r'^service/$', service, name='service'),
    re_path(r'^contact_us/$', contact_us, name='contact_us'),
    re_path(r'^confirm/$', confirm, name='confirm'),
    re_path(r'^inter_confirm/$', inter_confirm, name='inter_confirm'),
    re_path(r'^confirm_password/$', confirm_password, name='confirm_password'),
    re_path(r'^subscribe/$', subscribe, name='subscribe'),


    # transactions
    re_path(r'^', include('transactions.urls', namespace='transactions')),


]


if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
        )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
        )
