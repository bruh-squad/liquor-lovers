from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from rest_framework import viewsets, status, filters
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .serializers import PartySerializer, PartyInvitationSerializer, PartyRequestSerializer
from .models import Party, PartyInvitation, PartyRequest

User = get_user_model()


class PartyViewSet(viewsets.ModelViewSet):
    lookup_field = 'public_id'
    queryset = Party.objects.all().order_by('id')
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']

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
        queryset = list(filter(lambda p: p.can_see_party(request.user), self.filter_queryset(self.get_queryset())))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def list_participant(self, request, *args, **kwargs):
        """
        Lists all the parties that a user is a participant of.
        """
        queryset = list(filter(lambda p: request.user in p.participants.all(), self.filter_queryset(self.get_queryset())))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def list_mine(self, request, *args, **kwargs):
        """
        Lists all the parties that the user is owner of.
        """
        queryset = self.filter_queryset(request.user.parties_where_im_owner.all())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Updates a party. Returns a 403 Forbidden error if the request user is not the owner of the party.
        """
        if self.get_object().owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = request.data | {'owner_public_id': request.user.public_id}
        serializer = self.get_serializer(self.get_object(), data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates a party. Returns a 403 Forbidden error if the request user is not the owner of the party.
        """
        if self.get_object().owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Deletes an existing party object if the user is the owner.
        """
        party = self.get_object()

        if party.owner != request.user and request.user not in party.participants.all():
            return Response(status=status.HTTP_403_FORBIDDEN)

        if party.owner != request.user:
            party.participants.remove(request.user)
            party.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        self.perform_destroy(party)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def filter_queryset(self, queryset):
        party_range = self.request.query_params.get('range')
        if party_range is not None:
            point = self.request.headers.get('Point')
            if point is None:
                raise ValidationError({"msg": "Point header is missing."})

            location = GEOSGeometry(point)
            queryset = queryset.filter(
                location__distance_lt=(location, Distance(m=party_range))
            )

        return super().filter_queryset(queryset)


class PartyInvitationViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk'
    queryset = PartyInvitation.objects.all()
    serializer_class = PartyInvitationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Handles creation of party invitation.
        """
        party = self.get_party()

        if request.user != party.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data | {'party_public_id': party.public_id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def accept(self, request, *args, **kwargs):
        """
        Handles the acceptance of a party invitation by the current user.
        """
        invitation = self.get_object()

        if request.user != invitation.receiver:
            return Response(status=status.HTTP_204_NO_CONTENT)

        invitation.accept()
        return Response(status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        Retrieves the list of party invitations for the party.
        """
        party = self.get_party()

        if request.user != party.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)

        queryset = self.filter_queryset(self.get_queryset().filter(party=party))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def list_mine(self, request, *args, **kwargs):
        """
        Retrieves the list of party invitations for the current user.
        """
        queryset = self.filter_queryset(self.get_queryset().filter(receiver=request.user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Handles deletion of party invitation.
        """
        invitation = self.get_object()
        party = self.get_party()

        if request.user not in [party.owner, invitation.receiver]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(invitation)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_party(self):
        return get_object_or_404(Party, public_id=self.kwargs['party_public_id'])


class PartyRequestViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk'
    queryset = PartyRequest.objects.all()
    serializer_class = PartyRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Handles creation of party request.
        """
        party = self.get_party()

        if not party.can_see_party(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data | {'party_public_id': party.public_id,
                                                              'sender_public_id': request.user.public_id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def accept(self, request, *args, **kwargs):
        """
        Handles the acceptance of a party request.
        """
        party = self.get_party()
        party_request = self.get_object()

        if request.user != party.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)

        party_request.accept()
        return Response(status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        Retrieves the list of party requests for the party.
        """
        party = self.get_party()

        if request.user != party.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)

        queryset = self.filter_queryset(self.get_queryset().filter(party=party))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def list_mine(self, request, *args, **kwargs):
        """
        Retrieves the list of party invitations for the current user.
        """
        queryset = self.filter_queryset(self.get_queryset().filter(sender=request.user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Handles deletion of party invitation.
        """
        party_request = self.get_object()
        party = self.get_party()

        if request.user not in [party.owner, party_request.sender]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(party_request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_party(self):
        return get_object_or_404(Party, public_id=self.kwargs['party_public_id'])
