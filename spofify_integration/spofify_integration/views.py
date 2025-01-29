import typing as t

from django.contrib import messages
from django.db.models import QuerySet
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ArtistForm, TrackArtistForm
from .models import Album, Artist, Song
from .services import SpotifyService


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
        template_name="spotify_integration/song_details.html",
        context={
            "song": song,
            "album": song.album,
            "artists": song.artists.all(),
        },
    )


def fetch_artist_view(
    request: HttpRequest,
) -> t.Union[
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponse,
]:
    """
    Fetch Artist view.

    Args:
        request (HttpRequest): Request object passed from urls module.
    """
    if request.method == "POST":
        form = ArtistForm(data=request.POST)
        if form.is_valid():
            artist_name: str = form.cleaned_data["artist"]

            spotify_service: SpotifyService = SpotifyService()
            spotify_service.search_artist(
                artist=artist_name,
            )

            messages.success(
                request=request,
                message=f"Successfully fetched and added artist '{artist_name}'.",
            )
            return redirect(
                to="artist_list"
            )  # Redirect to songs list or any other desired page
        else:
            messages.error(
                request=request,
                message="Invalid input. Please correct the errors below.",
            )
    else:
        form = ArtistForm()

    return render(
        request=request,
        template_name="spotify_integration/fetch_artist_form.html",
        context={"form": form},
    )


def fetch_track_artist_view(
    request: HttpRequest,
) -> t.Union[
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponse,
]:
    """
    Fetch track view.

    Args:
        request (HttpRequest): Request object passed from urls module.
    """
    if request.method == "POST":
        form = TrackArtistForm(data=request.POST)
        if form.is_valid():
            artist_name: str = form.cleaned_data["artist"]
            track_name: str = form.cleaned_data["track_name"]

            spotify_service: SpotifyService = SpotifyService()
            spotify_service.search_artist_and_song(
                artist=artist_name,
                track_name=track_name,
            )

            messages.success(
                request=request,
                message=f"Successfully fetched and added '{track_name}' by '{artist_name}'.",
            )
            return redirect(
                to="song_list"
            )  # Redirect to songss list or any other desired page
        else:
            messages.error(
                request=request,
                message="Invalid input. Please correct the errors below.",
            )
    else:
        form = TrackArtistForm()

    return render(
        request=request,
        template_name="spotify_integration/fetch_track_artist_form.html",
        context={"form": form},
    )


def fetch_artist_albums_view(
    request: HttpRequest,
) -> t.Union[
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponse,
]:
    """
    Fetch track view.

    Args:
        request (HttpRequest): Request object passed from urls module.
    """
    if request.method == "POST":
        form = ArtistForm(data=request.POST)
        if form.is_valid():
            artist_name: str = form.cleaned_data["artist"]

            spotify_service: SpotifyService = SpotifyService()
            spotify_service.search_all_albums_by_artist(
                artist=artist_name,
            )

            messages.success(
                request=request,
                message=f"Successfully fetched and added all albums by '{artist_name}'.",
            )
            return redirect(
                to="album_list"
            )  # Redirect to songs list or any other desired page
        else:
            messages.error(
                request=request,
                message="Invalid input. Please correct the errors below.",
            )
    else:
        form = ArtistForm()

    return render(
        request=request,
        template_name="spotify_integration/fetch_artist_albums_form.html",
        context={"form": form},
    )


def fetch_all_songs_from_an_artist(
    request: HttpRequest,
) -> t.Union[
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponse,
]:
    """
    Fetch track view.

    Args:
        request (HttpRequest): Request object passed from urls module.
    """
    if request.method == "POST":
        form = ArtistForm(data=request.POST)
        if form.is_valid():
            artist_name: str = form.cleaned_data["artist"]

            spotify_service: SpotifyService = SpotifyService()
            spotify_service.search_all_songs_from_an_artist(
                artist=artist_name,
            )

            messages.success(
                request=request,
                message=f"Successfully fetched and added all albums by '{artist_name}'.",
            )
            return redirect(
                to="song_list"
            )  # Redirect to songs list or any other desired page
        else:
            messages.error(
                request=request,
                message="Invalid input. Please correct the errors below.",
            )
    else:
        form = ArtistForm()

    return render(
        request=request,
        template_name="spotify_integration/fetch_all_songs_from_an_artist.html",
        context={"form": form},
    )
