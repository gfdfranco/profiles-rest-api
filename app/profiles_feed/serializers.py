"""
Serializers for profiles feed APIs
"""
from rest_framework import serializers

from core.models import ProfilesFeed


class ProfilesFeedSerializer(serializers.ModelSerializer):
    """Serializer for profiles feeds."""

    class Meta:
        model = ProfilesFeed
        fields = ['id', 'description']
        read_only_fields = ['id']
