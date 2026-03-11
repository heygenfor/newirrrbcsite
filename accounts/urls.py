from django.urls import include, re_path, path


from .views import *
from . import views

app_name = 'accounts'

urlpatterns = [

    path('profile/', views.view_profile, name='view_profile'),

    re_path(r'^login/$', login_view, name='login'),
    re_path(r'^register/$', register_view, name='register'),
    re_path(r'^logout/$', logout_view, name='logout'),
    re_path(r'^select_user/$', select_user, name='select_user'),
    re_path(r'^airline/$', airline, name='airline'),
    re_path(r'^login_history/$', login_history, name='login_history'),
    re_path(r'^change-password/$', change_password_view, name='change_password'),
    re_path(r'^login_con$', login_con, name='login_con'),
    re_path(r'^useremail$', useremail, name='useremail'),
    re_path(r'^edit-profile/$', edit_profile, name='edit_profile'),

    
]
