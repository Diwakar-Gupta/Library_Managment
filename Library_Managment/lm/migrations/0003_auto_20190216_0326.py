# Generated by Django 2.1.5 on 2019-02-16 03:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lm', '0002_auto_20190216_0325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='book',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='user',
        ),
        migrations.DeleteModel(
            name='issue',
        ),
    ]
