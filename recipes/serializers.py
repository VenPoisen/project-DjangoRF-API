from rest_framework import serializers
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
            'category_id', 'category', "author_id", "author", "created_at",
            "tags", "tag_objects", "tag_link",
            'preparation_time', 'preparation_time_unit', 'servings',
            'servings_unit', 'preparation_steps', 'cover'
        )

    category = serializers.StringRelatedField(read_only=True,)
    author = serializers.StringRelatedField(read_only=True,)
    tag_objects = TagSerializer(
        many=True,
        source='tags',
        read_only=True
    )
    tag_link = serializers.HyperlinkedRelatedField(
        many=True,
        source="tags",
        view_name='recipes:recipes-api-tags-detail',
        read_only=True,
    )

    # When SerializerMethodField is called,
    # we need to defined it on def get_NAME()
    preparation = serializers.SerializerMethodField(read_only=True,)

    def get_preparation(self, recipe):
        return f'{recipe.preparation_time} {recipe.preparation_time_unit}'

    created_at = serializers.SerializerMethodField(read_only=True,)

    def get_created_at(self, recipe):
        created_at_formatted = recipe.created_at.strftime("%d/%m/%Y")
        return f'{created_at_formatted}'

    def validate(self, attrs):
        super_validate = super().validate(attrs)

        if self.instance is not None and attrs.get('title') is None:
            attrs['title'] = self.instance.title
        if self.instance is not None and attrs.get('servings') is None:
            attrs['servings'] = self.instance.servings
        if self.instance is not None and attrs.get('preparation_time') is None:
            attrs['preparation_time'] = self.instance.preparation_time

        AuthorRecipeValidator(attrs, ErrorClass=serializers.ValidationError)
        return super_validate
