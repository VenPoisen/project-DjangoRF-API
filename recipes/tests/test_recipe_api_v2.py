from django.urls import reverse
from rest_framework import test
from recipes.tests.test_recipe_base import RecipeMixin
from unittest.mock import patch


class RecipeAPIv2Test(test.APITestCase, RecipeMixin):
    def get_recipe_reverse_url(self, query_string=''):
        api_url = reverse("recipes:recipes-api-list") + query_string
        return api_url

    def get_recipe_api_list(self, query_string=''):
        api_url = self.get_recipe_reverse_url(query_string)
        response = self.client.get(api_url)
        return response

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
        api_url = self.get_recipe_reverse_url()
        response = self.client.post(api_url)
        self.assertEqual(response.status_code, 401)
