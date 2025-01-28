from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Album, Artist, Song


# Home view (optional, links to major sections)
def home(request: HttpRequest) -> HttpResponse:
    """
    Home view.

    Args:
        request (HttpRequest): Request object passed from urls module.

    Returns:
        HttpResponse: Response object with home page template.
    """
    return render(
        request=request,
        template_name="spotify_integration/home.html",
    )


# Artist Views
def artist_list(request: HttpRequest) -> HttpResponse:
    """
    Artist List view.

    Args:
        request (HttpRequest): Request object passed from urls module.

    Returns:
        HttpResponse: Response object with artists template.
    """
    artists: QuerySet[Artist] = Artist.objects.all()
    return render(
        request=request,
        template_name="spotify_integration/artists.html",
        context={"artists": artists},
    )


def artist_detail(request: HttpRequest, artist_id: int) -> HttpResponse:
    """
    Artist Detail view.

    Args:
        request (HttpRequest): Request object passed from urls module.
        artist_id (int): Artist id passed from urls module.

    Returns:
        HttpResponse: Response object with artists details template.
    """
    artist: Artist = get_object_or_404(klass=Artist, id=artist_id)
    # albums is the related name of the many-to-many field in the album field
    albums: QuerySet[Album] = artist.albums.all()
    songs: QuerySet[Song] = artist.songs.all()  # Songs by this artist
    return render(
        request=request,
        template_name="spotify_integration/artist_details.html",
        context={
            "artist": artist,
            "albums": albums,
            "songs": songs,
        },
    )


# Album Views
def album_list(request: HttpRequest) -> HttpResponse:
    """
    Album List view.

    Args:
        request (HttpRequest): Request object passed from urls module.

    Returns:
        HttpResponse: Response object with albums template.
    """
    albums: QuerySet[Album] = Album.objects.all()
    return render(
        request=request,
        template_name="spotify_integration/albums.html",
        context={"albums": albums},
    )


def album_detail(request: HttpRequest, album_id: int) -> HttpResponse:
    """
    Album Detail view.

    Args:
        request (HttpRequest): Request object passed from urls module.
        album_id (int): Album id passed from urls module.

    Returns:
        HttpResponse: Response object with album detail template.
    """
    album: Album = get_object_or_404(klass=Album, id=album_id)
    songs: QuerySet[Song] = album.songs.all()  # Songs in this album
    return render(
        request=request,
        template_name="spotify_integration/album_detail.html",
        context={
            "album": album,
            "songs": songs,
            "artists": album.artists.all(),
        },
    )


# Song Views
def song_list(request: HttpRequest) -> HttpResponse:
    """
    Song List view.

    Args:
        request (HttpRequest): Request object passed from urls module.

    Returns:
        HttpResponse: Response object with Song template.
    """
    songs: QuerySet[Song] = Song.objects.all()
    return render(
        request=request,
        template_name="spotify_integration/songs.html",
        context={"songs": songs},
    )


def song_detail(request: HttpRequest, song_id: int) -> HttpResponse:
    """
    Song Detail view.

    Args:
        request (HttpRequest): Request object passed from urls module.
        album_id (int): Song id passed from urls module.

    Returns:
        HttpResponse: Response object with song detail template.
    """
    song: Song = get_object_or_404(klass=Song, id=song_id)
    return render(
        request=request,
        template_name="spotify_integration/song_detail.html",
        context={
            "song": song,
            "album": song.album,
            "artists": song.artists.all(),
        },
    )
