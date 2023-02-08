from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .serializers import PartySerializer
from .models import Party


User = get_user_model()


class PartyViewSet(viewsets.ModelViewSet):
    lookup_field = 'public_id'
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Creates a new party object and associates the owner to the current user.
        """
        request.data['owner_public_id'] = request.user.public_id
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a party object if the user is allowed to see it.
        """
        party = self.get_object()

        if not party.can_see_party(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(party)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Lists all the parties that a user can see.
        """
        queryset = filter(lambda p: p.can_see_party(request.user), self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def list_mine(self, request, *args, **kwargs):
        """
        Lists all the parties that the user is owner of.
        """
        queryset = request.user.parties_where_im_owner
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Deletes an existing party object if the user is the owner.
        """
        if self.get_object().owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)
