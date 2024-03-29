from django.urls import include, path
from rest_framework import routers

from .views import SubscribeListViewSet, SubscribeViewSet

app_name = 'users'

router = routers.DefaultRouter()

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscribeListViewSet.as_view({'get': 'list'}),
        name='subscribe-list'
    ),
    path(
        r'users/<int:id>/subscribe/',
        SubscribeViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='subscribe'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
