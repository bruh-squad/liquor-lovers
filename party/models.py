import uuid

from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from LiquorLovers.utils import uuid_upload_to

User = get_user_model()


class Party(models.Model):
    class PrivacyStatus(models.IntegerChoices):
        PRIVATE = 1, _('Private')
        PUBLIC = 2, _('Public')
        SECRET = 3, _('Secret')

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parties_where_im_owner')
    name = models.TextField(max_length=100)
    privacy_status = models.IntegerField(choices=PrivacyStatus.choices, default=PrivacyStatus.PRIVATE)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to=uuid_upload_to('parties'), default='defaults/parties/default.png')
    participants = models.ManyToManyField(User, related_name='parties')
    localization = models.PointField(null=False, blank=False)
    start_time = models.DateTimeField()
    stop_time = models.DateTimeField()

    def __str__(self):
        return f'{self.owner.email} - {self.name}'

    def can_see_party(self, user):
        if self.privacy_status == self.PrivacyStatus.SECRET:
            return user in self.participants.all() or user == self.owner

        if self.privacy_status == self.PrivacyStatus.PRIVATE:
            return self.owner.friends_list.is_friend(user) or user == self.owner

        return True

    def add_participant(self, participant):
        self.participants.add(participant)
        self.save()

    def delete(self, using=None, keep_parents=False):
        if self.image.name != self.image.field.default:
            self.image.delete()

        return super().delete(using, keep_parents)


class PartyInvitation(models.Model):
    party = models.ForeignKey(Party, related_name='invitations', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='party_invitations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'Invitation to {self.party.name} to {self.receiver.username}'

    def accept(self):
        self.party.add_participant(self.receiver)
        self.delete()

    def reject(self):
        self.delete()


class PartyRequest(models.Model):
    party = models.ForeignKey(Party, related_name='requests', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='party_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'Request from {self.user.username} to {self.party.name}'

    def accept(self):
        self.party.add_participant(self.sender)
        self.delete()

    def reject(self):
        self.delete()
