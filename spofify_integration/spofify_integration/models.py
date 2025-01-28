from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Artist(models.Model):
    """
    Model for music artists.
    """

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    """
    Model for albums.
    """

    class Meta:
        unique_together = ("name", "release_date")

    name = models.CharField(max_length=255)
    release_date = models.DateField()
    # A related_name attribute is the name of the reverse relationship used to
    # access Album objects from Artist objects.
    artists = models.ManyToManyField(to=Artist, related_name="albums", blank=True)
    type = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Song(models.Model):
    """
    Model for songs.
    """

    name = models.CharField(max_length=255)
    artists = models.ManyToManyField(to=Artist, related_name="songs", blank=True)
    album = models.ForeignKey(Album, related_name="songs", on_delete=models.CASCADE)
    release_date = models.DateField()
    popularity = models.IntegerField(
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=100),
        ],
        help_text="Popularity score should be between 0 and 100.",
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.album.name if self.album else 'Single'})"
