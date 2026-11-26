from django.urls import path
from . import views

app_name = 'passgen'

urlpatterns = [
    path('passgen', views.index, name='passgen'),
    path('passgen/export/<str:file_format>/', views.export_passwords, name='export_passwords'),
]
