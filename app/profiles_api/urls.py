"""
URL mappings for the user API.
"""
from django.urls import path

from profiles_api import views


app_name = 'profiles_api'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
]
