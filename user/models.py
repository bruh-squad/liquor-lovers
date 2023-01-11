import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

from LiquorLovers.utils import uuid_upload_to
from user.managers import CustomUserManager


class User(AbstractUser):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_of_birth = models.DateField(blank=False)
    email = models.EmailField(unique=True)
    pfp = models.ImageField(upload_to=uuid_upload_to('pfp'), default='defaults/pfps/default.png')

    username = None

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']

    def __str__(self):
        return self.email

    def delete(self, using=None, keep_parents=False):
        if self.pfp.name != self.pfp.field.default:
            self.pfp.delete()

        return super().delete(using, keep_parents)

