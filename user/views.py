from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, CreateUserSerializer
from friend.serializers import FriendSerializer


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'public_id'
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves the current user's information.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        if request.query_params.get('q') is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['GET'])
    def retrieve_other(self, request, *args, **kwargs):
        """
        Retrieves information for a user specified by public_id.
        """
        user = self.get_object()

        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Handles the updating of the current user's information.
        """
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Handles partial updating of the current user's information.
        """
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Handles deletion of the current user's account.
        """
        self.perform_destroy(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'create' or self.action == 'retrieve_other':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve_other':
            return FriendSerializer
        elif self.action == 'create':
            return CreateUserSerializer
        return UserSerializer
