# Generated by Django 2.1.5 on 2019-02-16 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lm', '0008_book_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='mobile_number',
        ),
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
