from rest_framework import serializers
from django.contrib.auth.models import User
from tag.models import Tag
from .models import Recipe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "title", "description", 'preparation',
                  'category', "author", "tags", "tag_objects", "tag_link")

    category = serializers.StringRelatedField()
    tag_objects = TagSerializer(
        many=True,
        source='tags'
    )
    tag_link = serializers.HyperlinkedRelatedField(
        many=True,
        source="tags",
        queryset=Tag.objects.all(),
        view_name='recipes:recipe_api_v2_tag',
    )

    # When SerializerMethodField is called,
    # we need to defined it on def get_NAME()
    preparation = serializers.SerializerMethodField()

    def get_preparation(self, recipe):
        return f'{recipe.preparation_time} {recipe.preparation_time_unit}'
