import shutil
import tempfile

from django.conf import settings
from django.urls import reverse
from recipes.models import (Favourites, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag)
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, override_settings
from users.models import CustomUser

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

CREATE_USER_DICT = dict(
    username='HasNoName',
    email='HasNoName@hasnoname.ru',
    first_name='auth',
    last_name='auth',
    password='authuser'
)
NOT_AUTHOR_USER_DICT = dict(
    username='NoAuthor',
    email='NoAuthor@noauthor.ru',
    first_name='noauth',
    last_name='noauth',
    password='noauthuser'
)
COOKING_TIME = 30
AMOUNT_INGREDIENT = 5
TEST_IMAGE = (
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUg'
    'AAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD'
    '///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4b'
    'AAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
)
CONTENT_TYPE = 'text/csv'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestRecipeURL(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.TAG = Tag.objects.create(
            name='Test tag',
            color='#FFFF',
            slug='Test slug'
        )

        cls.INGREDIENT = Ingredient.objects.create(
            name='Test ingredient',
            measurement_unit='Test unit'
        )

        cls.USER = CustomUser.objects.create_user(
            **CREATE_USER_DICT
        )

        cls.RECIPE = Recipe.objects.create(
            author=cls.USER,
            name='Test name',
            image='Test image',
            text='Test text',
            cooking_time=COOKING_TIME
        )
        cls.RECIPE.tags.add(cls.TAG)
        IngredientRecipe.objects.create(
            ingredient=cls.INGREDIENT,
            recipe=cls.RECIPE,
            amount=AMOUNT_INGREDIENT
        )
        cls.RECIPE.ingredients.add(cls.INGREDIENT)

        cls.guest_client = APIClient()

        cls.auth_client = APIClient()
        cls.auth_client.force_authenticate(user=cls.USER)
        cls.NOTAUTHOR = CustomUser.objects.create_user(
            **NOT_AUTHOR_USER_DICT
        )
        cls.notauthor_client = APIClient()
        cls.notauthor_client.force_authenticate(user=cls.NOTAUTHOR)

        cls.URL_DICT = {
            'tag-list': reverse('recipes:tag-list'),
            'tag-detail': reverse(
                'recipes:tag-detail',
                kwargs={'pk': f'{cls.TAG.pk}'}
            ),
            'ingredient-list': reverse('recipes:ingredient-list'),
            'ingredient-detail': reverse(
                'recipes:ingredient-detail',
                kwargs={'pk': f'{cls.INGREDIENT.pk}'}
            ),
            'recipe-list': reverse('recipes:recipe-list'),
            'recipe-detail': reverse(
                'recipes:recipe-detail',
                kwargs={'pk': f'{cls.RECIPE.pk}'}
            ),
        }
        cls.CREATE_RECIPE_DICT = dict(
            tags=[cls.TAG.id],
            ingredients=[
                {'id': cls.INGREDIENT.id, 'amount': AMOUNT_INGREDIENT}
            ],
            name='Test name3',
            image=TEST_IMAGE,
            text='Test text2',
            cooking_time=COOKING_TIME
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def create_obj(self, model, url):
        '''Метод для создания объекта в базе данных.'''
        count = model.objects.count()
        pk = Recipe.objects.first().id
        response = self.auth_client.post(url.format(pk))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(model.objects.count(), count + 1)
        self.assertEqual(model.objects.first().recipe.name, 'Test name')

    def delete_obj(self, model, url):
        '''Метод для удаления объекта в базе данных.'''
        count = model.objects.count()
        pk = Recipe.objects.first().id
        response = self.auth_client.delete(url.format(pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(model.objects.count(), count - 1)

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
                elif method == 'patch':
                    response = self.guest_client.patch(adress)
                else:
                    response = self.guest_client.delete(adress)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED
                )

    def test_guest_url(self):
        '''Тест доступа к страницам открытым для любого пользователя.'''
        for adress in self.URL_DICT.values():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_create_recipe_url(self):
        '''Тест создания рецепта аутентифицированным пользователем.'''
        recipe_count = Recipe.objects.count()
        response = self.auth_client.post(
            self.URL_DICT['recipe-list'],
            data=self.CREATE_RECIPE_DICT,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), recipe_count + 1)
        self.assertEqual(Recipe.objects.get(id=2).name, 'Test name3')

    def test_auth_patch_url(self):
        '''Тест обновления рецепта автором.'''
        patch_recipe_dict = self.CREATE_RECIPE_DICT
        patch_recipe_dict['name'] = 'Test name4'
        pk = Recipe.objects.last().id
        url = reverse(
            'recipes:recipe-detail',
            kwargs={'pk': pk}
        )
        response = self.auth_client.patch(
            url,
            data=patch_recipe_dict,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Recipe.objects.get(id=pk).name, 'Test name4')

    def test_auth_recipe_delete_url(self):
        '''Тест удаления рецепта автором.'''
        recipe_count = Recipe.objects.count()
        pk = Recipe.objects.last().id
        url = reverse(
            'recipes:recipe-detail',
            kwargs={'pk': pk}
        )
        response = self.auth_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), recipe_count - 1)

    def test_favourites_auth_create_url(self):
        '''Тест добавления рецепта в избранное.'''
        url = '/api/recipes/{}/favorite/'
        self.create_obj(Favourites, url)

    def test_favourites_auth_delete_url(self):
        '''Тест удаления рецепта из избранного.'''
        url = '/api/recipes/{}/favorite/'
        self.create_obj(Favourites, url)
        self.delete_obj(Favourites, url)

    def test_shoppinglist_auth_create_url(self):
        '''Тест добавления рецепта в список покупок.'''
        url = '/api/recipes/{}/shopping_cart/'
        self.create_obj(ShoppingList, url)

    def test_shoppinglist_auth_delete_url(self):
        '''Тест удаления рецепта из списка покупок.'''
        url = '/api/recipes/{}/shopping_cart/'
        self.create_obj(ShoppingList, url)
        self.delete_obj(ShoppingList, url)

    def test_shoppinglist_auth_get_url(self):
        '''Тест скачивания списка покупок в формате CSV.'''
        create_url = '/api/recipes/{}/shopping_cart/'
        self.create_obj(ShoppingList, create_url)
        get_url = '/api/recipes/download_shopping_cart/'
        response = self.auth_client.get(get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.content.decode('utf-8').split(',')
        self.assertEqual(int(data[6][:1]), AMOUNT_INGREDIENT)
        content_type = response.__dict__['_headers']['content-type'][1]
        self.assertEqual(content_type, CONTENT_TYPE)

    def test_guest_post_not_acsess_url(self):
        '''
        Тест отсутствия доступа к
        созданию объектов в базе данных
        у неаутентифицированного пользователя.
        '''
        pk = Recipe.objects.first().id
        post_not_acsess_url = [
            self.URL_DICT['recipe-list'],
            f'/api/recipes/{pk}/favorite/',
            f'/api/recipes/{pk}/shopping_cart/'
        ]
        self.start_subtest(post_not_acsess_url, 'post')

    def test_guest_delete_not_acsess_url(self):
        '''
        Тест отсутствия доступа к
        удалению объектов в базе данных
        у неаутентифицированного пользователя.
        '''
        pk = Recipe.objects.first().id
        delete_not_acsess_url = [
            self.URL_DICT['recipe-detail'],
            f'/api/recipes/{pk}/favorite/',
            f'/api/recipes/{pk}/shopping_cart/'
        ]
        self.start_subtest(delete_not_acsess_url, 'delete')

    def test_guest_patch_not_acsess_url(self):
        '''
        Тест отсутствия доступа к
        обновлению объектов в базе данных
        у неаутентифицированного пользователя.
        '''
        patch_not_acsess_url = [self.URL_DICT['recipe-detail']]
        self.start_subtest(patch_not_acsess_url, 'patch')

    def test_guest_get_not_acsess_url(self):
        '''
        Тест отсутствия доступа к
        скачиванию списка покупок
        у неаутентифицированного пользователя.
        '''
        get_not_acsess_url = ['/api/recipes/download_shopping_cart/']
        self.start_subtest(get_not_acsess_url, 'get')

    def test_not_author_patch_not_acsess_url(self):
        '''
        Тест отсутствия доступа к
        обновлению рецепта у пользователя
        не являющегося автором этого рецепта.
        '''
        url = self.URL_DICT['recipe-detail']
        response = self.notauthor_client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_author_delete_not_acsess_url(self):
        '''
        Тест отсутствия доступа к
        удалению рецепта у пользователя
        не являющегося автором этого рецепта.
        '''
        url = self.URL_DICT['recipe-detail']
        response = self.notauthor_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
