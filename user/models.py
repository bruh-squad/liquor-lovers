import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from LiquorLovers.utils import uuid_upload_to
from user.managers import CustomUserManager


class User(AbstractUser):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_of_birth = models.DateField(blank=False)
    email = models.EmailField(unique=True, editable=False)
    pfp = models.ImageField(upload_to=uuid_upload_to('pfps'), default='defaults/pfps/default.png')
    username = models.CharField(null=False,
                                blank=False,
                                max_length=150,
                                unique=True,
                                editable=False,
                                validators=[UnicodeUsernameValidator()])

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'date_of_birth']

    def __str__(self):
        return self.email

    def delete(self, using=None, keep_parents=False):
        if self.pfp.name != self.pfp.field.default:
            self.pfp.delete()

        return super().delete(using, keep_parents)
