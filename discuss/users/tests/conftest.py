import factory
from faker import Factory as FakerFactory
from pytest_factoryboy import register

from users.models import User

faker = FakerFactory.create()


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.LazyAttributeSequence(lambda a, s: f'{faker.name()} {s}')
    email = factory.LazyAttribute(lambda a: faker.email())

    class Meta:
        model = User
