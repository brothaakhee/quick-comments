# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.test import APITestCase
from rest_framework import status

from django.core.urlresolvers import reverse
from django.core.cache import cache as default_cache

from comments.factories import CommentFactory, ContentFactory
from comments.models import Comment, Content


class CommentsTestCase(APITestCase):

    def setUp(self):
        self.test_content = ContentFactory(
            slug='test-url',
            content='test content'
        )

    def tearDown(self):
        default_cache.clear()

    def test_comment_creation_for_content_exists(self):
        '''
        Tests that if some piece of content exists, we can post a comment for
        it
        '''
        initial_count = Comment.objects.count()
        route = reverse('comments-list')
        payload = {
            'username': 'test',
            'content_url': 'test-url',
            'comment': 'hello'
        }

        response = self.client.post(route, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            Comment.objects.count(),
            initial_count + 1,
        )

        last_comment = Comment.objects.all().last()
        self.assertEqual(last_comment.content.slug, self.test_content.slug)

    def test_comment_creation_for_content_not_exists(self):
        '''
        Tests that we can post a comment for content that does not exist, and
        the endpoint will create that content url automagically.
        '''
        initial_comment_count = Comment.objects.count()
        initial_content_count = Content.objects.count()

        route = reverse('comments-list')
        payload = {
            'username': 'test',
            'content_url': 'a-new-url',
            'comment': 'hello'
        }

        response = self.client.post(route, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            Comment.objects.count(),
            initial_comment_count + 1,
        )

        last_comment = Comment.objects.all().last()
        self.assertNotEqual(last_comment.content.slug, self.test_content.slug)

        self.assertEqual(
            Content.objects.count(),
            initial_content_count + 1,
        )
        new_content = Content.objects.get(slug='a-new-url')

    def test_global_throttling(self):
        '''
        Tests that too many requests in a short period of time will result in
        getting throttled.
        '''
        route = reverse('comments-list')

        for i in range(0, 20):
            response = self.client.get(route)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(route)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )

    def test_throttle_recent_duplicate_comment(self):
        '''
        Tests that if a user posts a comment with the same text as another
        comment posted within the last 24 hours, that user is then locked
        out for a while.
        '''
        route = reverse('comments-list')

        payload = {
            'username': 'test',
            'content_url': 'test-url',
            'comment': 'same comment'
        }

        response = self.client.post(route, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        initial_comment_count = Comment.objects.count()

        payload = {
            'username': 'diff',
            'content_url': 'a-diff-url',
            'comment': 'same comment'
        }

        response = self.client.post(route, payload)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )

        self.assertEqual(
            Comment.objects.count(),
            initial_comment_count
        )

        response = self.client.get(route)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )

    def test_throttle_excessive_commenting(self):
        '''
        Tests that if a user posts more than 2 comments within a minute, that
        user is throttled.
        '''
        route = reverse('comments-list')

        payload = {
            'username': 'test',
            'content_url': 'test-url',
            'comment': 'hello'
        }

        response = self.client.post(route, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payload['comment'] = 'another'

        response = self.client.post(route, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        after_two_comment_count = Comment.objects.count()

        payload['comment'] = 'and another'

        response = self.client.post(route, payload)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )

        self.assertEqual(
            Comment.objects.count(),
            after_two_comment_count
        )

        response = self.client.get(route)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )

    def test_override_throttle_configurations(self):
        '''
        Tests that the system can be configured to override the default values
        for the throttling rates and lockout timings.
        '''
        pass
