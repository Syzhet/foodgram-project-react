from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from users.models import CustomUser, SubscribeModel

CREATE_USER_DICT = dict(
    email='TestUser@testuser.ru',
    username='TestUser',
    first_name='test',
    last_name='test',
    password='testuser'
)

CREATE_ANOTHER_USER_DICT = dict(
    email="Another@another.ru",
    username="Anotheruser",
    first_name="another",
    last_name="another",
    password="anotheruser"
)


class TestRecipeURL(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = APIClient()

        cls.USER = CustomUser.objects.create_user(
            **CREATE_USER_DICT
        )
        cls.auth_client = APIClient()
        cls.auth_client.force_authenticate(user=cls.USER)

        cls.URL_DICT = {
            'user-list': reverse('users:customuser-list'),
            'user-detail': reverse(
                'users:customuser-detail',
                kwargs={'id': cls.USER.id}
            ),
            'user-login': '/api/auth/token/login/',
            'user-logout': '/api/auth/token/logout/',
            'user-setpassword': '/api/users/set_password/',
            'user-me': reverse('users:customuser-me'),
            'subscribe-list': reverse('users:subscribe-list'),
            'subscribe': reverse(
                'users:subscribe',
                kwargs={'id': cls.USER.id}
            )
        }

    def create_another_user(self):
        '''Создание дополнительного пользователя.'''
        url = self.URL_DICT['user-list']
        return self.guest_client.post(url, data=CREATE_ANOTHER_USER_DICT)

    def create_token(self):
        '''Создание токена для дополнительного пользователя.'''
        data = dict(
            password=CREATE_ANOTHER_USER_DICT['password'],
            email=CREATE_ANOTHER_USER_DICT['email']
        )
        token_url = self.URL_DICT['user-login']
        return self.guest_client.post(token_url, data=data, format='json')

    def create_subscribe(self):
        '''Создание подписки на дополнительного пользователя.'''
        self.create_another_user()
        pk = CustomUser.objects.first().id
        url = reverse(
            'users:subscribe',
            kwargs={'id': pk}
        )
        return self.auth_client.post(url)

    def start_subtest(self, adress_list, method='get'):
        '''
        Проверка группы адресов на доступность
        для неаутентифицированного пользователя.
        '''
        for adress in adress_list:
            with self.subTest(adress=adress):
                if method == 'get':
                    response = self.guest_client.get(adress)
                elif method == 'post':
                    response = self.guest_client.post(adress)
                else:
                    response = self.guest_client.delete(adress)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED
                )

    def test_guest_admin_redirect_url(self):
        '''
        Тест доступа для неаутентифицированного пользователя
        к странице входа админ-зоны проекта.
        '''
        response = self.guest_client.get('/admin/')
        self.assertRedirects(response, '/admin/login/?next=/admin/')

    def test_guest_api_users_list_url(self):
        '''
        Тест доступа для неаутентифицированного пользователя
        к списку пользователей.
        '''
        response = self.guest_client.get(self.URL_DICT['user-list'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_api_users_detail_url(self):
        '''
        Тест доступа для аутентифицированного пользователя
        к профилю пользователя.
        '''
        response = self.auth_client.get(self.URL_DICT['user-detail'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_url(self):
        '''
        Тест возможности создания пользователя.
        '''
        count_users = CustomUser.objects.count()
        response = self.create_another_user()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), count_users + 1)
        self.assertEqual(
            CustomUser.objects.first().email,
            'Another@another.ru'
        )

    def test_create_token_auth_url(self):
        '''
        Тест возможности создания токена.
        '''
        count_tokens = Token.objects.count()
        self.create_another_user()
        response = self.create_token()
        user = CustomUser.objects.first()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), count_tokens + 1)
        self.assertEqual(
            response.data['auth_token'],
            Token.objects.get(user=user).key
        )

    def test_delete_token_auth_url(self):
        '''
        Тест возможности удаления токена.
        '''
        self.create_another_user()
        self.create_token()
        count_tokens = Token.objects.count()
        url = self.URL_DICT['user-logout']
        user = CustomUser.objects.first()
        token = Token.objects.get(user=user)
        test_del_token_client = APIClient(user=user)
        test_del_token_client.credentials(
            HTTP_AUTHORIZATION='Token ' + token.key
        )
        response = test_del_token_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Token.objects.count(), count_tokens - 1)

    def test_change_password_auth_url(self):
        '''
        Тест возможности смены пароля
        для аутентифицированного пользователя.
        '''
        url = self.URL_DICT['user-setpassword']
        data = dict(
            new_password='newpaaword',
            current_password=CREATE_USER_DICT['password']
        )
        response = self.auth_client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_auth_users_me_url(self):
        '''
        Тест доступа пользователя
        к собственноу профилю.
        '''
        response = self.auth_client.get(self.URL_DICT['user-me'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_subscribe_auth_url(self):
        '''
        Тест возможности создания подписки
        для аутентифицированного пользователя
        на другого пользователя.
        '''
        count_subscribe = SubscribeModel.objects.count()
        response = self.create_subscribe()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SubscribeModel.objects.count(), count_subscribe + 1)
        self.assertEqual(response.data['username'], 'Anotheruser')

    def test_delete_subscribe_auth_url(self):
        '''
        Тест возможности удаления подписки
        для аутентифицированного пользователя.
        '''
        self.create_subscribe()
        count_subscribe = SubscribeModel.objects.count()
        pk = CustomUser.objects.first().id
        url = reverse(
            'users:subscribe',
            kwargs={'id': pk}
        )
        response = self.auth_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            SubscribeModel.objects.count(),
            count_subscribe - 1
        )

    def test_user_subscribes_auth_url(self):
        '''
        Тест просмотра списка подписок
        для аутентифицированного пользователя.
        '''
        self.create_subscribe()
        response = self.auth_client.get(self.URL_DICT['subscribe-list'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['username'],
            'Anotheruser'
        )

    def test_guest_users_get_not_acsess_url(self):
        '''
        Тест отсутствия доступа к закрытым адресам
        у неаутентифицированного пользователя
        при get запросе.
        '''
        get_not_acsess_url = [
            self.URL_DICT['user-detail'],
            self.URL_DICT['user-me'],
            self.URL_DICT['subscribe-list']
        ]
        self.start_subtest(get_not_acsess_url, 'get')

    def test_guest_users_post_not_acsess_url(self):
        '''
        Тест отсутствия доступа к закрытым адресам
        у неаутентифицированного пользователя
        при post запросе.
        '''
        post_not_acsess_url = [
            self.URL_DICT['user-logout'],
            self.URL_DICT['user-setpassword'],
            self.URL_DICT['subscribe']
        ]
        self.start_subtest(post_not_acsess_url, 'post')

    def test_guest_users_delete_not_acsess_url(self):
        '''
        Тест отсутствия доступа к закрытым адресам
        у неаутентифицированного пользователя
        при delete запросе.
        '''
        delete_not_acsess_url = [self.URL_DICT['subscribe']]
        self.start_subtest(delete_not_acsess_url, 'delete')
