from django.shortcuts import get_object_or_404

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin
)
from rest_framework.response import Response
from rest_framework import status

from .models import SubscribeModel, CustomUser
from .serializers import SubscribeSerializer
from .pagination import CustomLimitPaginator


ERROR_MESSAGE_SUBSCRIBE_SELF = 'errors: Нельзя поодписаться на себя'
ERROR_MESSAGE_SUBSCRIBE_EXISTS = 'errors: Вы уже подписаны на пользователя'
ERROR_MESSAGE_NO_SUBSCRIBE = 'errors: Вы не подписаны на пользователя'


class SubscribeListViewSet(
    GenericViewSet,
    ListModelMixin,
):

    serializer_class = SubscribeSerializer
    pagination_class = CustomLimitPaginator

    def get_queryset(self):
        return CustomUser.objects.filter(follower__author=self.request.user)


class SubscribeViewSet(
    GenericViewSet,
    CreateModelMixin,
    DestroyModelMixin
):
    queryset = CustomUser.objects.all()
    serializer_class = SubscribeSerializer

    def create(self, request, **kwargs):
        follower = request.user
        author_id = kwargs.get('id')
        author = get_object_or_404(self.queryset, id=author_id)
        if author == follower:
            return Response(
                ERROR_MESSAGE_SUBSCRIBE_SELF,
                status=status.HTTP_400_BAD_REQUEST
            )
        if SubscribeModel.objects.filter(
            author=author,
            follower=follower
        ).exists():
            return Response(
                ERROR_MESSAGE_SUBSCRIBE_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
            )
        SubscribeModel.objects.create(
            author=author,
            follower=follower
        )
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, **kwargs):
        author = get_object_or_404(CustomUser, id=kwargs.get('id'))
        follower = request.user
        subscribe = SubscribeModel.objects.filter(
            author=author,
            follower=follower
        )
        if subscribe.exists():
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            ERROR_MESSAGE_NO_SUBSCRIBE,
            status=status.HTTP_400_BAD_REQUEST
        )
