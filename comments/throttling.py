import os
import time

from django.utils import timezone
from django.core.cache import cache as default_cache
from rest_framework import throttling

from comments.models import Comment


class ExcessCommentsThrottle(throttling.SimpleRateThrottle):
    """
    Throttle a user for posting too many comments within a certain timeframe.

    Defaults to 2 per minute and locks user out for 5 minutes.
    """
    lockout = int(os.environ.get('EXCESS_COMMENTS_LOCKOUT', 300))
    rate = os.environ.get('EXCESS_COMMENTS_RATE', '2/min')
    scope = 'excess_comment'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

    def allow_request(self, request, view):
        """
        Implement the check to see if the request should be throttled.
        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= self.now - self.lockout:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return False
        if view.action == 'create':
            self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.lockout)
        return True

    def wait(self):
        """
        Returns the recommended next request time in seconds.
        """
        if self.history:
            remaining_duration = self.lockout - (self.now - self.history[-1])
        else:
            remaining_duration = self.lockout

        available_requests = self.num_requests - len(self.history) + 1
        if available_requests <= 0:
            return None

        return remaining_duration / float(available_requests)


class RecentDuplicateCommentThrottle(throttling.BaseThrottle):
    """
    Throttle a user for if they submit a comment that is an exact** duplicate
    of an existing comment posted in the last x hours.

    Note: Only the actual comment is compared, and not the username or content
    it was posted for

    Defaults to last 24 hours and 60 second lockout.
    """
    lockout = int(os.environ.get('DUPLICATE_COMMENT_LOCKOUT', 60))
    hours = int(os.environ.get('DUPLICATE_COMMENT_HOURS', 24))

    scope = 'recent_dupe'
    cache_format = 'throttle_%(scope)s_%(ident)s'
    cache = default_cache
    timer = time.time

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

    def allow_request(self, request, view):
        self.now = self.timer()
        self.key = self.get_cache_key(request, view)

        self.locked_out = self.cache.get(self.key)
        if self.locked_out:
            return False

        if view.action == 'create':
            x_hours_ago = timezone.now() - timezone.timedelta(hours=self.hours)

            comment = request.data.get('comment')
            recent_duplicate_comments = Comment.objects.filter(
                comment=comment,
                created__gte=x_hours_ago
            )
            if recent_duplicate_comments:
                self.cache.set(self.key, self.now, self.lockout)
                return False

        return True

    def wait(self):
        """
        Returns the recommended next request time in seconds.
        """
        if self.locked_out:
            remaining_duration = self.lockout - (self.now - self.locked_out)
        else:
            remaining_duration = self.lockout

        return remaining_duration
