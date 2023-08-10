"""
Tests for profiles feed APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import ProfilesFeed

from profiles_feed.serializers import ProfilesFeedSerializer


FEED_URL = reverse('profiles_feed:profilesfeed-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('profiles_feed:profilesfeed-detail', args=[recipe_id])


def create_profiles_feed(user, **params):
    """Create and return a sample feed."""
    defaults = {
        'description': 'Sample description',
    }
    defaults.update(params)

    feed = ProfilesFeed.objects.create(user=user, **defaults)
    return feed


class PublicProfilesFeedAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(FEED_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProfilesFeedApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_profiles_feeds(self):
        """Test retrieving a list of feeds."""
        create_profiles_feed(user=self.user)
        create_profiles_feed(user=self.user)

        res = self.client.get(FEED_URL)

        feeds = ProfilesFeed.objects.all().order_by('-id')
        serializer = ProfilesFeedSerializer(feeds, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_profiles_feed_list_limited_to_user(self):
        """Test list of profiles feed is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_profiles_feed(user=other_user)
        create_profiles_feed(user=self.user)

        res = self.client.get(FEED_URL)

        feeds = ProfilesFeed.objects.filter(user=self.user)
        serializer = ProfilesFeedSerializer(feeds, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_profiles_feed_detail(self):
        """Test get profiles feed detail."""
        feed = create_profiles_feed(user=self.user)

        url = detail_url(feed.id)
        res = self.client.get(url)

        serializer = ProfilesFeedSerializer(feed)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a profiles feed."""
        payload = {
            'description': 'Sample description',
        }
        res = self.client.post(FEED_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        feed = ProfilesFeed.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(feed, k), v)
        self.assertEqual(feed.user, self.user)
