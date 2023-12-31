"""
Views for the profiles feed APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import ProfilesFeed
from profiles_feed import serializers


class ProfilesFeedViewSet(viewsets.ModelViewSet):
    """View for manage profiles feed APIs."""
    serializer_class = serializers.ProfilesFeedSerializer
    queryset = ProfilesFeed.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve profiles feeds for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new profiles feed."""
        serializer.save(user=self.request.user)
