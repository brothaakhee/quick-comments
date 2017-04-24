# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Content(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(blank=True, null=True)


class Comment(models.Model):
    content = models.ForeignKey(Content, related_name='comments')
    username = models.CharField(max_length=100)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
