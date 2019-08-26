from django.db import models

# Create your models here.

# Look at https://docs.djangoproject.com/en/2.2/intro/tutorial02/ when ready to implement the database
# Look at admin.py

class Song(models.Model):
    """Define data base entity of a song, capable of linking between spotify and apple music."""

    isrc = models.CharField(primary_key=True, max_length=12)
    spotify_id = models.CharField(max_length=30, default=None, null=True)
    apple_music_id = models.CharField(max_length=30,default=None, null=True)