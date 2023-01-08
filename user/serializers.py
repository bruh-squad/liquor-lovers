from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['public_id', 'email', 'first_name', 'last_name', 'date_of_birth', 'pfp', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('password') is not None:
            validated_data['password'] = make_password(validated_data['password'])

        return super().update(instance, validated_data)


class FriendSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['public_id', 'first_name', 'last_name', 'date_of_birth', 'pfp']
