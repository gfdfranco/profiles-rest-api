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


def detail_url(feed_id):
    """Create and return a profiles feed detail URL."""
    return reverse('profiles_feed:profilesfeed-detail', args=[feed_id])


def create_profiles_feed(user, **params):
    """Create and return a sample feed."""
    defaults = {
        'description': 'Sample description',
    }
    defaults.update(params)

    feed = ProfilesFeed.objects.create(user=user, **defaults)
    return feed


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='user@example.com', password='test123')
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
        other_user = create_user(email='other@example.com', password='test123')
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

    def test_create_profiles_feed(self):
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

    def test_partial_update(self):
        """Test partial update of a profiles feed."""
        feed = create_profiles_feed(
            user=self.user,
            description='This is a sample description.',
        )

        payload = {'description': 'New description'}
        url = detail_url(feed.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        feed.refresh_from_db()
        self.assertEqual(feed.description, payload['description'])
        self.assertEqual(feed.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the profiles feed user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        feed = create_profiles_feed(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(feed.id)
        self.client.patch(url, payload)

        feed.refresh_from_db()
        self.assertEqual(feed.user, self.user)

    def test_delete_profiles_feed(self):
        """Test deleting a profiles feed successful."""
        feed = create_profiles_feed(user=self.user)

        url = detail_url(feed.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProfilesFeed.objects.filter(id=feed.id).exists())

    def test_profiles_feed_other_users_profiles_feed_error(self):
        """Test trying to delete another users profiles feed gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        feed = create_profiles_feed(user=new_user)

        url = detail_url(feed.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ProfilesFeed.objects.filter(id=feed.id).exists())
