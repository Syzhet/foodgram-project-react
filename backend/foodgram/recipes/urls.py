from django.urls import path, include

from rest_framework import routers

from .views import TagViewSet


app_name = 'recipes'

router = routers.DefaultRouter()
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls))
]
