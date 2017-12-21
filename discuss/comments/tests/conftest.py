import random

import factory
from django.utils import timezone
from faker import Factory as FakerFactory
from pytest_factoryboy import register

from comments.models import Comment, CommentHistory
from users.tests.conftest import UserFactory

faker = FakerFactory.create()


@register
class FlatCommentFactory(factory.django.DjangoModelFactory):
    author = factory.SubFactory(UserFactory)

    content_type_id = 1
    object_id = 1

    content = factory.LazyAttribute(lambda a: faker.text())

    class Meta:
        model = Comment


class CommentFactory(FlatCommentFactory):
    parent = factory.SubFactory('comments.tests.conftest.CommentFactory')
    created_at = factory.LazyAttribute(lambda a: timezone.now())


@register
class CommentHistoryFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    comment = factory.SubFactory(FlatCommentFactory)

    action = factory.LazyAttribute(lambda a: random.choice([CommentHistory.CREATED, CommentHistory.UPDATED]))
    content = factory.LazyAttribute(lambda a: faker.text())

    class Meta:
        model = CommentHistory


register(CommentFactory)
