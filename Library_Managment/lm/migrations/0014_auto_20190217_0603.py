# Generated by Django 2.1.5 on 2019-02-17 06:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lm', '0013_auto_20190217_0601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lm.Book'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lm.Student'),
        ),
    ]