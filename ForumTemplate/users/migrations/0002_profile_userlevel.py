# Generated by Django 3.2.6 on 2021-08-22 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='userLevel',
            field=models.IntegerField(default=1),
        ),
    ]
