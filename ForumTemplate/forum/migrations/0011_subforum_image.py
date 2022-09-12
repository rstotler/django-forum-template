# Generated by Django 3.2.6 on 2021-09-11 17:59

from django.db import migrations, models
import forum.models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0010_remove_subforum_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='subforum',
            name='image',
            field=models.ImageField(default='subforum_icon/default.png', upload_to=forum.models.subforumIconImagePath),
        ),
    ]
