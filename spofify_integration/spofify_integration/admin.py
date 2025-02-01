from django.contrib import admin

from .models import Album, Artist, Genre, Song


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)  # Display the artist's name
    search_fields = ("name",)  # Add search functionality for artist names


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "artist_id", "id")  # Display the artist's name
    filter_horizontal = ("genres",)
    search_fields = ("name",)  # Add search functionality for artist names


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    # Attribute controls which fields or methods are displayed in the admin interface
    list_display = (
        "name",
        "album_type",
        "release_date",
        "get_artists",  # Custom method to display associated artists
        "album_id",
        "id",
    )
    # filter_horizontal is an attribute used to manage the ManyToManyField relationships
    filter_horizontal = ("artists",)
    # Add search functionality for album names
    search_fields = ("name",)
    # Add filter by release date
    list_filter = ("release_date",)

    def get_artists(self, obj: Album) -> str:
        return ", ".join([artist.name for artist in obj.artists.all()])

    # short_description is an attribute you can set on methods in ModelAdmin
    # classes to specify the column title in the Django admin interface.
    # In Django, it is common to add attributes to methods like this, but not
    # as common in Python in general.
    get_artists.short_description = "Artists"  # Column title in the admin


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "release_date",
        "popularity",
        "get_album",  # Custom method to display album name
        "get_artists",  # Custom method to display associated artists
        "id",
    )
    filter_horizontal = ("artists",)  # Enable horizontal widget for ManyToManyField
    search_fields = ("name",)  # Add search functionality for song names
    list_filter = (
        "release_date",
        "popularity",
    )  # Add filters by release date and popularity

    def get_album(self, obj: Song):
        return obj.album.name if "album" or "Album" in obj.album.type else "Single"

    get_album.short_description = "Album"  # Column title in the admin

    def get_artists(self, obj: Song):
        return ", ".join([artist.name for artist in obj.artists.all()])

    get_artists.short_description = "Artists"  # Column title in the admin
