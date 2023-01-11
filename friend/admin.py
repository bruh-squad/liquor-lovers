from django.contrib import admin

from .models import FriendsList, FriendInvitation

admin.site.register(FriendsList)
admin.site.register(FriendInvitation)
