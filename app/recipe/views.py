from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe
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





