import random

from django.core.management import BaseCommand

from comments.tests.conftest import FlatCommentFactory
from users.tests.conftest import UserFactory


def create_comment_tree(content_type_id, object_id, users):
    comment = FlatCommentFactory.create(
        content_type_id=content_type_id,
        object_id=object_id,
        author=random.choice(users)
    )

    tree_depth = random.randint(0, 101)
    possible_parent_ids = {
        0: [comment.pk]
    }
    for depth in range(tree_depth):
        k = random.randint(2, 4) if len(possible_parent_ids[depth]) > 1 else 1
        for parent_id in random.sample(possible_parent_ids[depth], k=k):
            replies_num = random.randint(4, 10)
            for _ in range(replies_num):
                comment = FlatCommentFactory.create(
                    content_type_id=content_type_id,
                    object_id=object_id,
                    author=random.choice(users),
                    parent_id=parent_id
                )
                try:
                    possible_parent_ids[depth + 1].append(comment.pk)
                except KeyError:
                    possible_parent_ids[depth + 1] = [comment.pk]


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = UserFactory.create_batch(200)

        for i in range(2):
            content_type_id = random.randint(3, 5)
            object_id = random.randint(3, 5)

            roots_comment_num = random.randint(20, 50)
            for _ in range(roots_comment_num):
                create_comment_tree(content_type_id, object_id, users)
