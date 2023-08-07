"""
Views for the user API.
"""
from rest_framework import generics

from profiles_api.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
