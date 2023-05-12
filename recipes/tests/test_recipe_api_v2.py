from django.urls import reverse
from rest_framework import test
from recipes.tests.test_recipe_base import RecipeMixin
from unittest.mock import patch


class RecipeAPIv2Mixin(RecipeMixin):
    def get_recipe_api_reverse_url_list(self, query_string=''):
        api_url = reverse("recipes:recipes-api-list") + query_string
        return api_url

    def get_recipe_api_list(self, query_string=''):
        api_url = self.get_recipe_api_reverse_url_list(query_string)
        response = self.client.get(api_url)
        return response

    def get_recipe_api_reverse_url_detail(self, pk=''):
        api_url = reverse("recipes:recipes-api-detail", args=(pk,))
        return api_url

    def get_auth_data(self, username='user', password='password'):
        user = self.make_author(username=username, password=password)
        api_token_url = reverse("recipes:token_obtain_pair")

        response = self.client.post(
            api_token_url,
            data={
                "username": username,
                "password": password,
            }
        )
        return {
            'jwt_access_token': response.data.get('access'),
            'jwt_refresh_token': response.data.get('refresh'),
            'user': user,
        }


class RecipeAPIv2Test(test.APITestCase, RecipeAPIv2Mixin):
    def test_recipe_api_list_returns_status_code_200(self):
        response = self.get_recipe_api_list()
        self.assertEqual(response.status_code, 200)

    @patch("recipes.views.api.RecipeAPIv2Pagination.page_size", new=7)
    def test_recipe_api_list_loads_correct_number_of_recipes(self):
        wanted_number_recipes = 7
        self.make_recipe_in_batch(qtd=wanted_number_recipes)

        response = self.get_recipe_api_list()
        qty_of_loaded_recipes = len(response.data.get('results'))

        self.assertEqual(wanted_number_recipes, qty_of_loaded_recipes)

    def test_recipe_api_list_do_not_show_not_published_recipes(self):
        recipes = self.make_recipe_in_batch(qtd=2)
        recipe_not_published = recipes[0]
        recipe_not_published.is_published = False
        recipe_not_published.save()

        response = self.get_recipe_api_list()
        self.assertEqual(len(response.data.get('results')), 1)

    @patch("recipes.views.api.RecipeAPIv2Pagination.page_size", new=10)
    def test_recipe_api_list_loads_recipes_by_category_id(self):
        # Create categories
        category_wanted = self.make_category(name='WANTED_CATEGORY')
        category_not_wanted = self.make_category(name='NOT_WANTED_CATEGORY')

        # Creates 10 recipes
        recipes = self.make_recipe_in_batch(qtd=10)
        # Change all recipes to the wanted category
        for recipe in recipes:
            recipe.category = category_wanted
            recipe.save()

        # Change ONE recipe to the NOT wanted category
        # As a result, this recipe should NOT show in the page
        recipes[0].category = category_not_wanted
        recipes[0].save()

        # Action: get recipes by wanted category
        response = self.get_recipe_api_list(
            query_string=f'?category_id={category_wanted.id}'
        )

        # We should only see recipes in wanted category
        self.assertEqual(len(response.data.get('results')), 9)

    def test_recipe_api_list_user_must_send_jwt_token_to_create_recipe(self):
        api_url = self.get_recipe_api_reverse_url_list()
        response = self.client.post(api_url)
        self.assertEqual(response.status_code, 401)

    def test_recipe_api_list_logged_user_can_create_a_recipe(self):
        raw_data = self.get_recipe_raw_data()
        auth_data = self.get_auth_data()
        jwt_access_token = auth_data.get('jwt_access_token')
        api_url = self.get_recipe_api_reverse_url_list()

        response = self.client.post(
            api_url, data=raw_data,
            HTTP_AUTHORIZATION=f"Bearer {jwt_access_token}",
        )

        self.assertEqual(response.status_code, 201)

    def test_recipe_api_list_logged_user_can_delete_a_recipe(self):
        # Create new user
        new_user = self.get_auth_data(
            username='test_delete',
            password='password',
        )

        # Make a recipe with the new user created
        # create_author=False to use the new user created
        recipe = self.make_recipe(
            create_author=False,
            author_data=new_user.get('user'),
        )

        jwt_access_token = new_user.get('jwt_access_token')
        api_url = self.get_recipe_api_reverse_url_detail(pk=recipe.id)

        response = self.client.delete(
            api_url,
            HTTP_AUTHORIZATION=f"Bearer {jwt_access_token}",
        )

        # Assertion 204 No content
        # Showing that the action delete succeed
        self.assertEqual(response.status_code, 204)

    def test_recipe_api_list_logged_user_cannot_delete_recipe_owned_by_another_user(self):
        # Make a recipe with new user
        # create_author=True to create new user
        recipe = self.make_recipe(
            create_author=True,
            author_data={
                'username': 'new_user',
                'password': 'password',
            },
        )

        # Create another user
        another_user = self.get_auth_data(
            username='cannot_delete',
            password='password',
        )

        # Get JWT token access for another user
        another_user_jwt_access_token = another_user.get('jwt_access_token')

        api_url = self.get_recipe_api_reverse_url_detail(pk=recipe.id)

        # Try to delete the recipe with another user token
        response = self.client.delete(
            api_url,
            HTTP_AUTHORIZATION=f"Bearer {another_user_jwt_access_token}",
        )

        # Assertion 403 Forbidden
        # Because another user cannot delete the recipe
        self.assertEqual(response.status_code, 403)

    def test_recipe_api_list_logged_user_can_update_a_recipe(self):
        # Make a recipe
        recipe = self.make_recipe()

        # Change the recipe user to match the token user
        auth_data = self.get_auth_data(username='test_patch')
        author = auth_data.get("user")
        recipe.author = author
        recipe.save()

        jwt_access_token = auth_data.get('jwt_access_token')
        recipe_detail_url = self.get_recipe_api_reverse_url_detail(
            pk=recipe.id)

        wanted_new_title = f'New title updated by {author.username}'

        # Action patch
        response = self.client.patch(
            recipe_detail_url,
            data={'title': wanted_new_title},
            HTTP_AUTHORIZATION=f"Bearer {jwt_access_token}",
        )

        # Assertion
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('title'), wanted_new_title)

    def test_recipe_api_list_logged_user_cannot_update_a_recipe_owned_by_another_user(self):
        # Make a recipe with one user
        recipe = self.make_recipe(
            author_data={'username': 'recipe_author_user'},
        )

        recipe_detail_url = self.get_recipe_api_reverse_url_detail(
            pk=recipe.id)

        # Get token access with another user
        another_user = self.get_auth_data(username='cant_update')
        another_user_jwt_access_token = another_user.get('jwt_access_token')

        # Action patch using authorization from another user
        response = self.client.patch(
            recipe_detail_url,
            data={},
            HTTP_AUTHORIZATION=f"Bearer {another_user_jwt_access_token}",
        )

        # Assertion 403 Forbidden
        # because another user cannot update the recipe
        self.assertEqual(response.status_code, 403)
