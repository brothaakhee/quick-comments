import factory

from comments.models import Comment, Content

class CommentFactory(factory.Factory):
    class Meta:
        model = Comment


class ContentFactory(factory.Factory):
    class Meta:
        model = Content
