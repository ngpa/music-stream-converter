# Generated by Django 2.2.4 on 2019-08-22 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='apple_music_id',
            field=models.CharField(default=None, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='song',
            name='spotify_id',
            field=models.CharField(default=None, max_length=30, null=True),
        ),
    ]
