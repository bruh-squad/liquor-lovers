from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers

from user.serializers import FriendSerializer
from .models import Party

User = get_user_model()


class PartySerializer(serializers.ModelSerializer):
    owner = FriendSerializer(read_only=True)
    owner_public_id = serializers.SlugRelatedField(
        source='owner', queryset=User.objects.all(), slug_field='public_id', write_only=True
    )

    participants = FriendSerializer(many=True, read_only=True)
    privacy_status_display = serializers.CharField(source='get_privacy_status_display', read_only=True)

    class Meta:
        model = Party
        geo_field = 'localization'
        fields = ['public_id',
                  'owner',
                  'owner_public_id',
                  'name',
                  'privacy_status',
                  'privacy_status_display',
                  'description',
                  'participants',
                  'localization',
                  'start_time',
                  'stop_time']

        read_only_fields = ('public_id', 'owner')

    def create(self, validated_data):
        validated_data['participants'] = validated_data.get('participants') or []

        validated_data['participants'].append(validated_data['owner'])
        return super().create(validated_data)

    def validate(self, data):
        if self.instance is not None and data['owner'] not in data['participants']:
            raise serializers.ValidationError(_('You can not remove yourself from participant list'))

        if data['start_time'] > data['stop_time']:
            raise serializers.ValidationError(_('Stop time must occur after start time'))

        return data
