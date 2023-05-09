from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from ..models import Recipe
from ..serializers import RecipeSerializer, TagSerializer
from ..permissions import IsOwner
from tag.models import Tag


class RecipeAPIv2Pagination(PageNumberPagination):
    page_size = 6


class RecipeAPIv2ViewSet(ModelViewSet):
    queryset = Recipe.objects.get_published()
    serializer_class = RecipeSerializer
    pagination_class = RecipeAPIv2Pagination
    permission_classes = [IsAuthenticatedOrReadOnly,]
    http_method_names = ["GET", "OPTIONS", "HEAD", "POST", "PATCH", "DELETE"]

    def get_queryset(self):
        qs = super().get_queryset()

        category_id = self.request.query_params.get('category_id', '')

        if category_id != '' and category_id.isnumeric():
            qs = qs.filter(category_id=category_id)

        return qs

    def get_object(self):
        pk = self.kwargs.get("pk", "")
        obj = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsOwner(),]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


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
