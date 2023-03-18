import datetime
from uuid import uuid4

from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from PIL import Image
from rest_framework.validators import UniqueValidator

from friend.serializers import FriendSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True, read_only=True, source='friends_list.friends')

    class Meta:
        model = User
        fields = ['public_id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'date_of_birth',
                  'pfp',
                  'friends',
                  'password']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        user = super().save(**kwargs)

        if user.pfp.name != user.pfp.field.default:
            image = Image.open(user.pfp)
            resized_image = image.resize((256, 256), Image.ANTIALIAS)
            resized_image.save(user.pfp.path)

        return user

    def create(self, validated_data):
        try:
            return User.objects.create_user(**validated_data)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        if validated_data.get('password') is not None:
            validated_data['password'] = make_password(validated_data['password'])

        return super().update(instance, validated_data)

    def validate_password(self, password):
        validate_password(password)
        return password

    def validate_date_of_birth(self, date_of_birth):
        if datetime.date.today() - date_of_birth < datetime.timedelta(days=18 * 365):
            raise serializers.ValidationError(_('The user must be an adult. '))
        return date_of_birth


class CreateUserSerializer(UserSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(User.objects.all())])
    username = serializers.CharField(max_length=150,
                                     validators=[UniqueValidator(User.objects.all())])

    class Meta:
        model = User
        fields = ['public_id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'date_of_birth',
                  'pfp',
                  'friends',
                  'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': False},
            'email': {'read_only': False}
        }
