from django.urls import path
from .views import generate_cards_view

app_name = 'cardhtml'

urlpatterns = [
    path('', generate_cards_view, name='generate_cards'),
]
