from django.db import models


class FriendsList(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE, related_name='friends_list')
    friends = models.ManyToManyField('user.User', blank=True)

    def __str__(self):
        return f'Friends list - {self.user.email}'

    def add_friend(self, friend):
        self.friends.add(friend)
        friend.friends_list.friends.add(self.user)

        self.save()

    def remove_friend(self, friend):
        self.friends.remove(friend)
        friend.friends_list.friends.remove(self.user)

        self.save()

    def is_friend(self, friend):
        return friend in self.friends.all()


class FriendInvitation(models.Model):
    sender = models.ForeignKey('user.User', on_delete=models.CASCADE)
    receiver = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='invitations')
    created_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'Friend invitation from f{self.sender.email} to {self.receiver.email}'

    def accept(self):
        self.sender.friends_list.add_friend(self.receiver)
        self.delete()

    def reject(self):
        self.delete()
