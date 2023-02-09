import datetime

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserTests(APITestCase):
    def test_create_user(self):
        url = '/users/'

        # need all properties
        data = {'email': 'email'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

        # check password strength
        data = {'email': 'email@email.com', 'username': 'username', 'password': 'password',
                'date_of_birth': '2000-01-01'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

        # check age
        data = {'email': 'email@email.com', 'username': 'username', 'password': 'password',
                'date_of_birth': '2018-01-01'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

        # everything should be fine
        data = {'email': 'email@email.com', 'username': 'username',
                'password': 'Password1234$!',
                'date_of_birth': '2000-01-01'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.filter(public_id=response.data['public_id']).exists())

        user = User.objects.get(public_id=response.data['public_id'])
        self.assertEqual(user.email, 'email@email.com')
        self.assertNotEqual(user.password, 'Password1234$!')
        self.assertEqual(user.date_of_birth, datetime.date(2000, 1, 1))

        data = {'email': 'email@email.com', 'username': 'username',
                'password': 'Password1234$!',
                'date_of_birth': '2000-01-01'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # try to log in
        url = '/auth/token/'

        # need all properties
        data = {'email': 'email@email.com', 'username': 'username',
                'password': 'Password1234$!'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {'email': 'email@email.com', 'username': 'username',
                'password': 'Password1234$!'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user(self):
        User.objects.create_user(email='email@email.com',
                                 username='username',
                                 password='Password1234$!',
                                 date_of_birth=datetime.date(2000, 1, 1))

        url = '/users/'

        data = {'username': 'new_username'}

        jwt = self.client.post('/auth/token/',
                               {'email': 'email@email.com', 'password': 'Password1234$!'},
                               format='json').data['access']

        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')
        self.assertEqual(User.objects.get(email='email@email.com').username, 'username')

        data = {'date_of_birth': '2001-01-01'}

        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(email='email@email.com').date_of_birth, datetime.date(2001, 1, 1))

    def test_retrieve(self):
        user = User.objects.create_user(email='email@email.com',
                                        username='username',
                                        password='Password1234$!',
                                        date_of_birth=datetime.date(2000, 1, 1))

        url = '/users/'

        jwt = self.client.post('/auth/token/',
                               {'email': 'email@email.com', 'password': 'Password1234$!'},
                               format='json').data['access']

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')
        self.assertEqual(str(user.public_id), response.data['public_id'])
        self.assertEqual(user.pfp.url, response.data['pfp'].replace('http://testserver', ''))
        self.assertEqual(str(user.date_of_birth), response.data['date_of_birth'])

    def test_retrieve_other(self):
        user = User.objects.create_user(email='email@email.com',
                                        username='username',
                                        password='Password1234$!',
                                        date_of_birth=datetime.date(2000, 1, 1))

        url = f'/users/{user.public_id}/'

        response = self.client.get(url, format='json')
        self.assertIsNone(response.data.get('email'))
        self.assertEqual(str(user.public_id), response.data['public_id'])
        self.assertEqual(user.pfp.url, response.data['pfp'].replace('http://testserver', ''))
        self.assertEqual(str(user.date_of_birth), response.data['date_of_birth'])

    def test_destroy_user(self):
        User.objects.create_user(email='email@email.com',
                                 username='username',
                                 password='Password1234$!',
                                 date_of_birth=datetime.date(2000, 1, 1))

        url = '/users/'

        jwt = self.client.post('/auth/token/',
                               {'email': 'email@email.com', 'password': 'Password1234$!'},
                               format='json').data['access']

        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)
