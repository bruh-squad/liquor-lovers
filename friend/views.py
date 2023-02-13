from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .serializers import FriendInvitationSerializer, FriendSerializer
from .models import FriendInvitation


User = get_user_model()


class FriendViewSet(viewsets.ModelViewSet):
    lookup_field = 'public_id'
    queryset = User.objects.all()
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Retrieves the list of friends for the current user.
        """
        queryset = request.user.friends_list.friends
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Removes a friend from the current user's friend list.
        """
        friend = self.get_object()

        if not request.user.friends_list.is_friend(friend):
            return Response({'detail': _('This user is not your friend. ')}, status=status.HTTP_400_BAD_REQUEST)

        request.user.friends_list.remove_friend(friend)

        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitationViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk'
    queryset = FriendInvitation.objects.all()
    serializer_class = FriendInvitationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new friend invitation.
        """
        serializer = self.get_serializer(data=request.data | {'sender_public_id': request.user.public_id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        Retrieves the list of friend invitations for the current user.
        """
        queryset = self.get_queryset().filter(receiver=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def list_from_me(self, request, *args, **kwargs):
        """
        Retrieves the list of friend invitations sent by the current user.
        """
        queryset = self.get_queryset().filter(sender=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def accept(self, request, *args, **kwargs):
        """
        Handles the acceptance of a friend invitation by the current user.
        """
        invitation = self.get_object()

        if request.user != invitation.receiver:
            return Response(status=status.HTTP_403_FORBIDDEN)

        invitation.accept()
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Handles the rejection of a friend invitation.
        """
        invitation = self.get_object()

        if request.user not in [invitation.sender, invitation.receiver]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        invitation.reject()
        return Response(status=status.HTTP_204_NO_CONTENT)
