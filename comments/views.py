# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework import viewsets, throttling
from comments.serializers import CommentSerializer, ContentSerializer
from comments.models import Comment, Content
from comments.throttling import (
    ExcessCommentsThrottle,
    RecentDuplicateCommentThrottle
)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    throttle_classes = (ExcessCommentsThrottle, RecentDuplicateCommentThrottle)


class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all()

    lookup_field = 'slug'
