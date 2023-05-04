from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Recipe
from ..serializers import RecipeSerializer, TagSerializer
from tag.models import Tag


class RecipeAPIv2Pagination(PageNumberPagination):
    page_size = 6


class RecipeAPIv2List(ListCreateAPIView):
    queryset = Recipe.objects.get_published()
    serializer_class = RecipeSerializer
    pagination_class = RecipeAPIv2Pagination


class RecipeAPIv2Detail(RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.get_published()
    serializer_class = RecipeSerializer
    pagination_class = RecipeAPIv2Pagination


@api_view()
def recipe_api_tag(request, pk):
    tag = get_object_or_404(
        Tag.objects.all(),
        pk=pk
    )
    serializer = TagSerializer(
        instance=tag,
        many=False,
    )

    return Response(serializer.data)
