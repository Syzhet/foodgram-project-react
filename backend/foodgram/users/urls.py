from django.urls import path, include

from rest_framework import routers


app_name = 'users'

router = routers.DefaultRouter()

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
