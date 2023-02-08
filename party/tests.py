import datetime
import json

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Party

User = get_user_model()


class PartyTest(APITestCase):
    def test_create_party(self):
        url = '/parties/'

        user = User.objects.create_user(email='user@user.com',
                                        password='Password&1976',
                                        date_of_birth=datetime.date(2000, 1, 1))

        data = {'email': user.email, 'password': 'Password&1976'}
        jwt = self.client.post('/auth/token/', data, format='json').data['access']

        data = {'name': 'party name',
                'privacy_status': '1',
                'description': 'description',
                'localization': 'POINT(10 10)',
                'start_time': timezone.datetime(year=2023, month=1, day=1, hour=20, minute=30).isoformat(),
                'stop_time': timezone.datetime(year=2023, month=1, day=2, hour=2, minute=30).isoformat()}

        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'party name')
        self.assertEqual(response.data['privacy_status'], 1)
        self.assertEqual(response.data['privacy_status_display'], 'Private')
        self.assertEqual(response.data['description'], 'description')
        self.assertEqual(response.data['localization'], 'SRID=4326;POINT (10 10)')
        self.assertEqual(response.data['start_time'], '2023-01-01T20:30:00Z')
        self.assertEqual(response.data['stop_time'], '2023-01-02T02:30:00Z')
        self.assertEqual(response.data['participants'][0]['public_id'], str(user.public_id))

    def test_list_parties(self):
        url = '/parties/'

        user = User.objects.create_user(email='user@user.com',
                                        password='Password&1976',
                                        date_of_birth=datetime.date(2000, 1, 1))

        party_user = User.objects.create_user(email='party_user@party_user.com',
                                              password='Password&1976',
                                              date_of_birth=datetime.date(2000, 1, 1))

        private_party = Party.objects.create(name='private_party name',
                                             owner=party_user,
                                             description='private_party description',
                                             privacy_status=Party.PrivacyStatus.PRIVATE,
                                             localization='POINT(12 12)',
                                             start_time=timezone.datetime(day=1, month=1, year=1, hour=22, minute=10,
                                                                          tzinfo=timezone.utc),
                                             stop_time=timezone.datetime(day=2, month=1, year=1, hour=4, minute=0,
                                                                         tzinfo=timezone.utc))

        public_party = Party.objects.create(name='public_party name',
                                            owner=party_user,
                                            description='public_party description',
                                            privacy_status=Party.PrivacyStatus.PUBLIC,
                                            localization='POINT(12 12)',
                                            start_time=timezone.datetime(day=1, month=1, year=1, hour=22, minute=10,
                                                                         tzinfo=timezone.utc),
                                            stop_time=timezone.datetime(day=2, month=1, year=1, hour=4, minute=0,
                                                                        tzinfo=timezone.utc))

        secret_party = Party.objects.create(name='secret_party name',
                                            owner=party_user,
                                            description='secret_party description',
                                            privacy_status=Party.PrivacyStatus.SECRET,
                                            localization='POINT(12 12)',
                                            start_time=timezone.datetime(day=1, month=1, year=1, hour=22, minute=10,
                                                                         tzinfo=timezone.utc),
                                            stop_time=timezone.datetime(day=2, month=1, year=1, hour=4, minute=0,
                                                                        tzinfo=timezone.utc))

        data = {'email': user.email, 'password': 'Password&1976'}
        jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')

        self.assertEqual(len(response.data), 1)

        user.friends_list.add_friend(party_user)

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')
        self.assertEqual(len(response.data), 2)

        data = {'email': party_user.email, 'password': 'Password&1976'}
        party_jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {party_jwt}')
        self.assertEqual(len(response.data), 3)

        response = self.client.get(f'{url}mine/', format='json', HTTP_AUTHORIZATION=f'Bearer {party_jwt}')
        self.assertEqual(len(response.data), 3)

        response = self.client.get(f'{url}mine/', format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')
        self.assertEqual(len(response.data), 0)

    def test_retrieve_party(self):
        url = '/parties/'

        user = User.objects.create_user(email='user@user.com',
                                        password='Password&1976',
                                        date_of_birth=datetime.date(2000, 1, 1))

        party_user = User.objects.create_user(email='party_user@party_user.com',
                                              password='Password&1976',
                                              date_of_birth=datetime.date(2000, 1, 1))

        private_party = Party.objects.create(name='private_party name',
                                             owner=party_user,
                                             description='private_party description',
                                             privacy_status=Party.PrivacyStatus.PRIVATE,
                                             localization='POINT(12 12)',
                                             start_time=timezone.datetime(day=1, month=1, year=1, hour=22, minute=10,
                                                                          tzinfo=timezone.utc),
                                             stop_time=timezone.datetime(day=2, month=1, year=1, hour=4, minute=0,
                                                                         tzinfo=timezone.utc))

        public_party = Party.objects.create(name='public_party name',
                                            owner=party_user,
                                            description='public_party description',
                                            privacy_status=Party.PrivacyStatus.PUBLIC,
                                            localization='POINT(12 12)',
                                            start_time=timezone.datetime(day=1, month=1, year=1, hour=22, minute=10,
                                                                         tzinfo=timezone.utc),
                                            stop_time=timezone.datetime(day=2, month=1, year=1, hour=4, minute=0,
                                                                        tzinfo=timezone.utc))

        data = {'email': user.email, 'password': 'Password&1976'}
        jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.get(f'{url}{private_party.public_id}', format='json',
                                   HTTP_AUTHORIZATION=f'Bearer {jwt}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'{url}{public_party.public_id}', format='json',
                                   HTTP_AUTHORIZATION=f'Bearer {jwt}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_party(self):
        url = '/parties/'

        user = User.objects.create_user(email='user@user.com',
                                        password='Password&1976',
                                        date_of_birth=datetime.date(2000, 1, 1))

        party_user = User.objects.create_user(email='party_user@party_user.com',
                                              password='Password&1976',
                                              date_of_birth=datetime.date(2000, 1, 1))

        party = Party.objects.create(name='private_party name',
                                     owner=user,
                                     description='private_party description',
                                     privacy_status=Party.PrivacyStatus.PRIVATE,
                                     localization='POINT(12 12)',
                                     start_time=timezone.datetime(day=1, month=1, year=1, hour=22, minute=10,
                                                                  tzinfo=timezone.utc),
                                     stop_time=timezone.datetime(day=2, month=1, year=1, hour=4, minute=0,
                                                                 tzinfo=timezone.utc))

        public_party = Party.objects.create(name='public_party name',
                                            owner=party_user,
                                            description='public_party description',
                                            privacy_status=Party.PrivacyStatus.PUBLIC,
                                            localization='POINT(12 12)',
                                            start_time=timezone.datetime(day=1, month=1, year=1, hour=22, minute=10,
                                                                         tzinfo=timezone.utc),
                                            stop_time=timezone.datetime(day=2, month=1, year=1, hour=4, minute=0,
                                                                        tzinfo=timezone.utc))

        data = {'email': user.email, 'password': 'Password&1976'}
        jwt = self.client.post('/auth/token/', data, format='json').data['access']

        response = self.client.delete(f'{url}{party.public_id}/', HTTP_AUTHORIZATION=f'Bearer {jwt}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Party.objects.count(), 1)

        response = self.client.delete(f'{url}{public_party.public_id}/', HTTP_AUTHORIZATION=f'Bearer {jwt}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Party.objects.count(), 1)
