from django.urls import reverse, path, include
from rest_framework.routers import DefaultRouter
from recipe import views

router = DefaultRouter()
router.register('recipes', views.BaseRecipeAttrViewSet)
router.register('tags', views.TagViewSet, basename='tag')
app_name = 'recipe'



urlpatterns = [
    path('', include(router.urls)),
]