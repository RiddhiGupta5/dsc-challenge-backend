# Generated by Django 2.2 on 2020-06-17 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20200616_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.URLField(default=None, null=True),
        ),
    ]
