from rest_framework import serializers
from django.contrib.auth.models import User
from tag.models import Tag
from .models import Recipe
from authors.validators import AuthorRecipeValidator


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id", "title", "description", 'preparation',
            'category', "author", "tags", "tag_objects", "tag_link",
            'preparation_time', 'preparation_time_unit', 'servings',
            'servings_unit', 'preparation_steps', 'cover'
        )

    category = serializers.StringRelatedField(read_only=True,)
    tag_objects = TagSerializer(
        many=True,
        source='tags',
        read_only=True
    )
    tag_link = serializers.HyperlinkedRelatedField(
        many=True,
        source="tags",
        view_name='recipes:recipe_api_v2_tag',
        read_only=True,
    )

    # When SerializerMethodField is called,
    # we need to defined it on def get_NAME()
    preparation = serializers.SerializerMethodField(read_only=True,)

    def get_preparation(self, recipe):
        return f'{recipe.preparation_time} {recipe.preparation_time_unit}'

    def validate(self, attrs):
        super_validate = super().validate(attrs)
        AuthorRecipeValidator(attrs, ErrorClass=serializers.ValidationError)
        return super_validate
