# Generated by Django 3.2.6 on 2021-08-17 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0005_alter_subforum_titleurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='viewCount',
            field=models.IntegerField(default=0),
        ),
    ]
