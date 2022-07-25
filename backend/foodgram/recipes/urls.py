from django.urls import path, include

from rest_framework import routers

from .views import (
    TagViewSet,
    IngredientViewSet,
)


app_name = 'recipes'

router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls))
]
