import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Genre(models.Model):
    """
    Model for music genres.
    """

    name = models.CharField(max_length=255, unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class Artist(models.Model):
    """
    Model for music artists.
    """

    class Meta:
        unique_together = (
            "name",
            "artist_id",
        )

    name = models.CharField(max_length=255)
    genres = models.ManyToManyField(
        to=Genre,
        related_name="artists",
        blank=True,
    )
    artist_id = models.CharField(max_length=255, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class Album(models.Model):
    """
    Model for albums.
    """

    class Meta:
        unique_together = (
            "name",
            "album_id",
        )

    name = models.CharField(max_length=255)
    release_date = models.DateField()
    # A related_name attribute is the name of the reverse relationship used to
    # access Album objects from Artist objects.
    artists = models.ManyToManyField(
        to=Artist,
        related_name="albums",
        blank=True,
    )
    album_type = models.CharField(max_length=255)
    album_id = models.CharField(max_length=255, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        return self.name


class Song(models.Model):
    """
    Model for songs.
    """

    class Meta:
        unique_together = (
            "name",
            "release_date",
        )

    name = models.CharField(max_length=255)
    artists = models.ManyToManyField(
        to=Artist,
        related_name="songs",
        blank=True,
    )
    album = models.ForeignKey(
        to=Album,
        related_name="songs",
        on_delete=models.CASCADE,
    )
    release_date = models.DateField()
    popularity = models.IntegerField(
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=100),
        ],
        help_text="Popularity score should be between 0 and 100.",
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        return f"{self.name} ({self.album.name if self.album else 'Single'})"


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # Other fields like created_at, etc.

    def __str__(self):
        return self.name


class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    # Ensure that the song is unique within the playlist
    class Meta:
        unique_together = (
            "playlist",
            "song",
        )  # Enforce uniqueness for each song in a playlist

    def __str__(self):
        return f"{self.playlist.name} - {self.song.name}"
