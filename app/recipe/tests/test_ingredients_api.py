"""test for ingredients API"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from core import models
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')
def detail_url(ingredient_id):
    """create and return an ingredient detail url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='test@example.com', password='testpass123'):
    """create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientAPITests(TestCase):
    """test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()
       


    def test_auth_required(self):
        """test auth is required"""

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    
    def test_retrieve_ingredient_list(self):
        """test retrieving a list of ingredients"""
        models.Ingredient.objects.create(user=self.user, name='Ingredient1')
        models.Ingredient.objects.create(user=self.user, name='Ingredient2')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = models.Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
   
   
    def test_ingredients_limited_to_user(self):
        """test that ingredients for the authenticated user are returned"""
        other_user = create_user(email='other@example.com')
        models.Ingredient.objects.create(user=other_user, name='Salt')
        ingredient = models.Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)
   
    # def test_create_ingredient(self):
    #     """Test creating an ingredient"""
    #     payload = {'name': 'Ingredient1'}
    #     response = self.client.post(INGREDIENTS_URL, payload)

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     ingredient = models.Ingredient.objects.get(id=response.data['id'])
    #     self.assertEqual(ingredient.name, payload['name'])
    #     self.assertEqual(ingredient.user, self.user)

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        ingredient = models.Ingredient.objects.create(
            user=self.user,
            name='Carrot'
        )
        payload = {'name': 'Cabbage'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        ingredient = models.Ingredient.objects.create(
            user=self.user,
            name='Ingredient1'
        )
        response = self.client.delete(reverse('recipe:ingredient-detail', args=[ingredient.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Ingredient.objects.filter(id=ingredient.id).exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = models.Ingredient.objects.create(user=self.user, name='Apple')
        ingredient2 = models.Ingredient.objects.create(user=self.user, name='Banana')
        recipe = models.Recipe.objects.create(
            user=self.user,
            title='Recipe1',
            time_minutes=10,
            price=5.00
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
    