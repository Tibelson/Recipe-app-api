from rest_framework import (viewsets, mixins,)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tags, Ingredient
from recipe import serializers



class BaseRecipeAttrViewSet(viewsets.ModelViewSet):
    "view for manage recipe APIs"
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')
    def get_serializer_class(self):
        """return the serializer class for request"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        
        return self.serializer_class
    def perform_create(self, serializer):
        """create a new recipe"""
        serializer.save(user=self.request.user)

class BaseAttrViewSet(mixins.DestroyModelMixin,mixins.UpdateModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    """base viewset for user owned recipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

class TagViewSet(BaseAttrViewSet):
    """manage tags in the database"""
    
    queryset = Tags.objects.all()
    serializer_class = serializers.TagSerializer

    
  
    
class IngredientViewSet(BaseAttrViewSet):
    """manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    
  
