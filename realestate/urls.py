from django.urls import path
from . import views

app_name = 'realestate'

urlpatterns = [
    # Property listing and detail
    path('', views.property_list, name='property_list'),
    path('property/<slug:slug>/', views.property_detail, name='property_detail'),
    path('type/<str:type_name>/', views.property_by_type, name='property_by_type'),
    
    # User applications
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
]