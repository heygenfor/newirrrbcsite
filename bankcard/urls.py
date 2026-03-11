from django.urls import path
from . import views

app_name = 'bankcard'

urlpatterns = [
    path('request/', views.card_request, name='card_request'),
    path('approve/<int:card_request_id>/', views.card_approval, name='card_approval'),
    path('user_cards/', views.user_cards, name='user_cards'),
    path('cards_types/', views.cards_types, name='cards_types'),
    path('approve_select_user/', views.approve_select_user, name='approve_select_user'),
]


