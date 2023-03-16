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

    def test_list(self):
        user1 = User.objects.create_user(email='email@email.com',
                                         username='username',
                                         password='Password1234$!',
                                         date_of_birth=datetime.date(2000, 1, 1))
        user2 = User.objects.create_user(email='johnny@email.com',
                                         username='johnny_star',
                                         password='Password1234$!',
                                         date_of_birth=datetime.date(2000, 1, 1))
        user3 = User.objects.create_user(email='bob@email.com',
                                         username='bobby_star',
                                         password='Password1234$!',
                                         date_of_birth=datetime.date(2000, 1, 1))
        user4 = User.objects.create_user(email='alice@email.com',
                                         username='alice',
                                         password='Password1234$!',
                                         date_of_birth=datetime.date(2000, 1, 1))

        url = f'/users/search/'

        jwt = self.client.post('/auth/token/',
                               {'email': 'email@email.com', 'password': 'Password1234$!'},
                               format='json').data['access']

        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, None)

        url = f'/users/search/?q=alice'
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], user4.username)

        url = f'/users/search/?q=tar'
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION=f'Bearer {jwt}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['username'], user2.username)
        self.assertEqual(response.data['results'][1]['username'], user3.username)

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
