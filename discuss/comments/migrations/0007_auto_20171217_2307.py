# Generated by Django 2.0 on 2017-12-17 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0006_auto_20171217_2304'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='comment',
            index_together={('content_type_id', 'object_id', 'is_deleted')},
        ),
    ]
