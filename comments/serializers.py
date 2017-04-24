from rest_framework import serializers
from comments.models import Comment, Content


class CommentSerializer(serializers.ModelSerializer):
    content_url = serializers.SlugField(write_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'content',
            'content_url',
            'username',
            'comment',
            'created'
        )
        read_only_fields = ('id', 'content', 'created')
        write_only_fields = ('content_url',)

    def create(self, validated_data):
        content_url = validated_data.pop('content_url')
        content, _ = Content.objects.get_or_create(slug=content_url)
        comment = Comment.objects.create(content=content, **validated_data)
        return comment


class ContentSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)

    class Meta:
        model = Content
        fields = (
            'id',
            'slug',
            'content',
            'comments'
        )
        read_only_fields = ('id', 'comments')

        lookup_field = 'slug'
