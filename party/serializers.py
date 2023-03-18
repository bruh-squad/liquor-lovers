from math import floor

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.utils.translation import gettext as _
from geopy.distance import distance
from rest_framework import serializers

from user.serializers import FriendSerializer
from .models import Party, PartyInvitation, PartyRequest

User = get_user_model()


class PartySerializer(serializers.ModelSerializer):
    owner = FriendSerializer(read_only=True)
    owner_public_id = serializers.SlugRelatedField(
        source='owner', queryset=User.objects.all(), slug_field='public_id', write_only=True
    )

    participants = FriendSerializer(many=True, read_only=True)
    privacy_status_display = serializers.CharField(source='get_privacy_status_display', read_only=True)

    distance = serializers.SerializerMethodField()

    class Meta:
        model = Party
        geo_field = 'location'
        fields = ['public_id',
                  'owner',
                  'owner_public_id',
                  'name',
                  'privacy_status',
                  'privacy_status_display',
                  'description',
                  'image',
                  'participants',
                  'location',
                  'distance',
                  'start_time',
                  'stop_time']

        read_only_fields = ('public_id', 'owner')

    def create(self, validated_data):
        validated_data['participants'] = validated_data.get('participants') or []

        validated_data['participants'].append(validated_data['owner'])
        return super().create(validated_data)

    def validate(self, data):
        if self.instance is not None and \
                (data.get('owner') or self.instance.owner) not in \
                data.get('participants', self.instance.participants.all()):
            raise serializers.ValidationError(_('You can not remove yourself from participant list. '))

        if data.get('start_time') is not None or data.get('stop_time') is not None:
            if data.get('start_time') > data.get('stop_time'):
                raise serializers.ValidationError(_('Stop time must occur after start time. '))

        return data

    def get_distance(self, obj):
        point = self.context['request'].headers.get('Point')
        if point is None:
            return 0

        point_location = GEOSGeometry(point)
        return floor(distance(obj.location, point_location).meters)


class PartyInvitationSerializer(serializers.ModelSerializer):
    party = PartySerializer(read_only=True)
    party_public_id = serializers.SlugRelatedField(
        source='party', queryset=Party.objects.all(), slug_field='public_id', write_only=True
    )

    receiver = FriendSerializer(read_only=True)
    receiver_public_id = serializers.SlugRelatedField(
        source='receiver', queryset=User.objects.all(), slug_field='public_id', write_only=True
    )

    class Meta:
        model = PartyInvitation
        fields = ['party', 'party_public_id', 'receiver', 'receiver_public_id', 'created_at']

    def validate(self, attrs):
        if attrs['receiver'] in attrs['party'].participants.all():
            raise serializers.ValidationError(_('User is already party participant. '))

        return attrs


class PartyRequestSerializer(serializers.ModelSerializer):
    party = PartySerializer(read_only=True)
    party_public_id = serializers.SlugRelatedField(
        source='party', queryset=Party.objects.all(), slug_field='public_id', write_only=True
    )

    sender = FriendSerializer(read_only=True)
    sender_public_id = serializers.SlugRelatedField(
        source='sender', queryset=User.objects.all(), slug_field='public_id', write_only=True
    )

    class Meta:
        model = PartyRequest
        fields = ['party', 'party_public_id', 'sender', 'sender_public_id', 'created_at']

    def validate(self, attrs):
        if attrs['sender'] in attrs['party'].participants.all():
            raise serializers.ValidationError(_('User is already party participant. '))

        return attrs
