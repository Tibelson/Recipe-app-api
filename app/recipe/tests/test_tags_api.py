"""Test for the tags API"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

from core.models import Recipe, Tags

from recipe.serializers import TagSerializer   

TAGS_URL = reverse('recipe:tag-list')
def create_user(**params):
    return get_user_model().objects.create_user(**params)

def detail_url(tag_id):
    """create and return a tag detail URL"""
    return reverse('recipe:tag-detail', args=[tag_id])  

class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    """Test the athorized user tags API"""

    def setUp(self):
        self.user = create_user(email='test@example.com',password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tags.objects.create(user=self.user,name='Vegan')
        Tags.objects.create(user=self.user,name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tags.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        other_user = create_user(email='other@example.com',password='testpass123')
        Tags.objects.create(user=other_user,name='Fruity')
        tag = Tags.objects.create(user=self.user,name='Comfort Food')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],tag.name)
        self.assertEqual(res.data[0]['id'],tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tags.objects.create(user=self.user,name='After Dinner') #seting up tag

        payload = {'name':'Dessert'} #request: updating the tag name
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """test deleteing a tag"""
        tag = Tags.objects.create(user=self.user,name='Breakfast') #create tag
    
        url = detail_url(tag.id) #get the tag/ list the tag
        res = self.client.delete(url) #user deletes

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tags.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """test listing tags to those assigned to recipes"""
        tag1 = Tags.objects.create(user=self.user,name='Breakfast')
        tag2 = Tags.objects.create(user=self.user,name='Lunch')
        recipe =Recipe.objects.create(
            user=self.user,
            title='Coriander eggs on toast',
            time_minutes=10,
            price=Decimal('5.00')
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only':1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags return a unique list"""
        tag = Tags.objects.create(user=self.user,name='Dinner')
        Tags.objects.create(user=self.user,name='Dessert')
        recipe1 =Recipe.objects.create(
            user=self.user,
            title='Pancakes',
            time_minutes=5,
            price=Decimal('3.00')
        )
        recipe1.tags.add(tag)
        recipe2 =Recipe.objects.create(
            user=self.user,
            title='Porridge',
            time_minutes=3,
            price=Decimal('2.00')
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only':1})

        self.assertEqual(len(res.data),1)