from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers

from .models import FriendsList, FriendInvitation


User = get_user_model()


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['public_id', 'username', 'first_name', 'last_name', 'date_of_birth', 'pfp']
        read_only_fields = ('public_id', 'first_name', 'last_name', 'date_of_birth', 'pfp')


class FriendsListSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True, read_only=True)

    class Meta:
        model = FriendsList
        fields = ['friends']


class FriendInvitationSerializer(serializers.ModelSerializer):
    sender = FriendSerializer(read_only=True)
    sender_public_id = serializers.SlugRelatedField(
        source='sender', queryset=User.objects.all(), slug_field='public_id', write_only=True
    )

    receiver = FriendSerializer(read_only=True)
    receiver_public_id = serializers.SlugRelatedField(
        source='receiver', queryset=User.objects.all(), slug_field='public_id', write_only=True
    )

    class Meta:
        model = FriendInvitation
        fields = ['id', 'sender', 'receiver', 'receiver_public_id', 'sender_public_id', 'created_at']

    def validate(self, attrs):
        invitation = FriendInvitation.objects.filter(sender=attrs['sender'],
                                                     receiver=attrs['receiver'])

        if invitation.exists():
            raise serializers.ValidationError(_('Invitation like this already exists. '))

        invitation = FriendInvitation.objects.filter(receiver=attrs['sender'],
                                                     sender=attrs['receiver'])

        if invitation.exists():
            raise serializers.ValidationError(_('The receiver already invited you. '))

        if attrs['sender'] == attrs['receiver']:
            raise serializers.ValidationError(_('You can not invite yourself. '))

        return attrs
