import datetime

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from friend.models import FriendInvitation

User = get_user_model()


class FriendTest(APITestCase):
    def test_list_friends(self):
        url = '/friends/'

        user = User.objects.create_user(email='user@user.com',
                                        username='username',
                                        password='Password&1976',
                                        date_of_birth=datetime.date(2000, 1, 1))

        friend = User.objects.create_user(email='friend@friend.com',
                                          username='friend',
                                          password='Password&1976',
                                          date_of_birth=datetime.date(2000, 1, 1))

        friend1 = User.objects.create_user(email='friend1@friend1.com',
                                           username='friend1',
                                           password='Password&1976',
                                           date_of_birth=datetime.date(2000, 1, 1))

        user.friends_list.add_friend(friend)
        user.friends_list.add_friend(friend1)

        self.assertEqual(len(user.friends_list.friends.all()), 2)
        self.assertEqual(len(friend.friends_list.friends.all()), 1)

        data = {'email': user.email, 'password': 'Password&1976'}
        jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')

        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['public_id'], str(friend.public_id))
        self.assertEqual(response.data['results'][1]['public_id'], str(friend1.public_id))

    def test_unfriend(self):
        url = '/friends/'

        user = User.objects.create_user(email='user@user.com',
                                        username='username',
                                        password='Password&1976',
                                        date_of_birth=datetime.date(2000, 1, 1))

        friend = User.objects.create_user(email='friend@friend.com',
                                          username='friend',
                                          password='Password&1976',
                                          date_of_birth=datetime.date(2000, 1, 1))

        friend1 = User.objects.create_user(email='friend1@friend1.com',
                                           username='friend1',
                                           password='Password&1976',
                                           date_of_birth=datetime.date(2000, 1, 1))

        user.friends_list.add_friend(friend)
        user.friends_list.add_friend(friend1)

        self.assertEqual(len(user.friends_list.friends.all()), 2)
        self.assertEqual(len(friend.friends_list.friends.all()), 1)

        data = {'email': user.email, 'password': 'Password&1976'}
        jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.delete(f'{url}{str(friend.public_id)}/',
                                      format='json',
                                      HTTP_AUTHORIZATION=f'Bearer {jwt}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(user.friends_list.friends.all()), 1)


class InvitationTests(APITestCase):
    def test_list_invitations(self):
        url = '/friends/invitations/'

        sender = User.objects.create_user(email='sender@sender.com',
                                          username='sender',
                                          password='Password&1976',
                                          date_of_birth=datetime.date(2000, 1, 1))

        receiver = User.objects.create_user(email='receiver@receiver.com',
                                            username='receiver',
                                            password='Password&1976',
                                            date_of_birth=datetime.date(2000, 1, 1))

        FriendInvitation.objects.create(sender=sender, receiver=receiver)

        data = {'email': receiver.email, 'password': 'Password&1976'}
        receiver_jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {receiver_jwt}')

        self.assertEqual(len(response.data['results']), 1)

    def test_list_from_me_invitations(self):
        url = '/friends/invitations/my/'

        sender = User.objects.create_user(email='sender@sender.com',
                                          username='sender',
                                          password='Password&1976',
                                          date_of_birth=datetime.date(2000, 1, 1))

        receiver = User.objects.create_user(email='receiver@receiver.com',
                                            username='receiver',
                                            password='Password&1976',
                                            date_of_birth=datetime.date(2000, 1, 1))

        FriendInvitation.objects.create(sender=sender, receiver=receiver)

        data = {'email': sender.email, 'password': 'Password&1976'}
        sender_jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {sender_jwt}')

        self.assertEqual(len(response.data['results']), 1)

    def test_create_invitation(self):
        url = '/friends/invitations/'

        sender = User.objects.create_user(email='sender@sender.com',
                                          username='sender',
                                          password='Password&1976',
                                          date_of_birth=datetime.date(2000, 1, 1))

        receiver = User.objects.create_user(email='receiver@receiver.com',
                                            username='receiver',
                                            password='Password&1976',
                                            date_of_birth=datetime.date(2000, 1, 1))

        data = {'email': sender.email, 'password': 'Password&1976'}
        sender_jwt = self.client.post('/auth/token/', data, format='json').data['access']

        data = {'email': receiver.email, 'password': 'Password&1976'}
        receiver_jwt = self.client.post('/auth/token/', data, format='json').data['access']

        data = {'receiver_public_id': str(receiver.public_id)}
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {sender_jwt}')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendInvitation.objects.count(), 1)

        data = {'receiver_public_id': str(receiver.public_id)}
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {sender_jwt}')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FriendInvitation.objects.count(), 1)

        data = {'receiver_public_id': str(sender.public_id)}
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {receiver_jwt}')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FriendInvitation.objects.count(), 1)

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {receiver_jwt}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['sender']['public_id'], str(sender.public_id))
        self.assertEqual(response.data['results'][0]['receiver']['public_id'], str(receiver.public_id))

    def test_invitation_reject(self):
        url = '/friends/invitations/'

        sender = User.objects.create_user(email='sender@sender.com',
                                          username='sender',
                                          password='Password&1976',
                                          date_of_birth=datetime.date(2000, 1, 1))

        receiver = User.objects.create_user(email='receiver@receiver.com',
                                            username='receiver',
                                            password='Password&1976',
                                            date_of_birth=datetime.date(2000, 1, 1))

        FriendInvitation.objects.create(sender=sender, receiver=receiver)

        data = {'email': sender.email, 'password': 'Password&1976'}
        sender_jwt = self.client.post('/auth/token/', data, format='json').data['access']

        data = {'email': receiver.email, 'password': 'Password&1976'}
        receiver_jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {receiver_jwt}')

        self.assertEqual(len(response.data['results']), 1)

        response = self.client.delete(f'{url}{response.data["results"][0]["id"]}/',
                                      format='json',
                                      HTTP_AUTHORIZATION=f'Bearer {receiver_jwt}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(sender in receiver.friends_list.friends.all())
        self.assertFalse(receiver in sender.friends_list.friends.all())

    def test_invitation_cancel(self):
        url = '/friends/invitations/'

        sender = User.objects.create_user(email='sender@sender.com',
                                          username='sender',
                                          password='Password&1976',
                                          date_of_birth=datetime.date(2000, 1, 1))

        receiver = User.objects.create_user(email='receiver@receiver.com',
                                            username='receiver',
                                            password='Password&1976',
                                            date_of_birth=datetime.date(2000, 1, 1))

        FriendInvitation.objects.create(sender=sender, receiver=receiver)

        data = {'email': sender.email, 'password': 'Password&1976'}
        sender_jwt = self.client.post('/auth/token/', data, format='json').data['access']

        data = {'email': receiver.email, 'password': 'Password&1976'}
        receiver_jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {receiver_jwt}')

        self.assertEqual(len(response.data['results']), 1)

        response = self.client.delete(f'{url}{response.data["results"][0]["id"]}/',
                                      format='json',
                                      HTTP_AUTHORIZATION=f'Bearer {sender_jwt}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(sender in receiver.friends_list.friends.all())
        self.assertFalse(receiver in sender.friends_list.friends.all())
