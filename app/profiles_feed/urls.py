"""
URL mappings for the profiles feed app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from profiles_feed import views


router = DefaultRouter()
router.register('profiles_feeds', views.ProfilesFeedViewSet)

app_name = 'profiles_feed'

urlpatterns = [
    path('', include(router.urls)),
]
