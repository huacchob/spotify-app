import typing as t

from django.contrib import messages
from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ArtistForm, SearchForm, TrackArtistForm
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
    sort_by = request.GET.get("sort_by", "name")  # Default to 'name'
    sort_order = request.GET.get("sort_order", "asc")  # Default to ascending order
    valid_sort_fields = ["name"]
    valid_sort_orders = ["asc", "desc"]

    # Validate the sorting parameters
    if sort_by not in valid_sort_fields:
        sort_by = "name"
    if sort_order not in valid_sort_orders:
        sort_order = "asc"

    # Prepare the ordering string
    ordering = f"{'-' if sort_order == 'desc' else ''}{sort_by}"

    # Initialize the search form and get the albums queryset
    form = SearchForm(data=request.GET)
    artists: QuerySet[Artist] = Artist.objects.all().order_by("name")

    # Apply search filtering if the form is valid
    if form.is_valid():
        query = form.cleaned_data.get("query")
        if query:
            artists = artists.filter(
                name__icontains=query,
            ) | artists.filter(
                artist_id__icontains=query,
            )

    # Apply sorting by ordering, and re-assign the sorted queryset to 'artists'
    artists = artists.order_by(ordering)

    # Paginate the artists
    paginator: Paginator = Paginator(object_list=artists, per_page=10)
    page_number: str | None = request.GET.get("page")
    page_obj: Page = paginator.get_page(number=page_number)

    # Return the rendered template with the context
    return render(
        request=request,
        template_name="spotify_integration/artists.html",
        context={
            "artists": page_obj.object_list,
            "page_obj": page_obj,
            "form": form,
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
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
    sort_by = request.GET.get("sort_by", "name")  # Default to 'name'
    sort_order = request.GET.get("sort_order", "asc")  # Default to ascending order
    valid_sort_fields = ["name", "release_date", "artists__name"]
    valid_sort_orders = ["asc", "desc"]

    # Validate the sorting parameters
    if sort_by not in valid_sort_fields:
        sort_by = "name"
    if sort_order not in valid_sort_orders:
        sort_order = "asc"

    # Prepare the ordering string
    ordering = f"{'-' if sort_order == 'desc' else ''}{sort_by}"

    # Initialize the search form and get the albums queryset
    form = SearchForm(data=request.GET)
    albums: QuerySet[Album] = Album.objects.all()

    # Apply search filtering if the form is valid
    if form.is_valid():
        query = form.cleaned_data.get("query")
        if query:
            albums = (
                albums.filter(name__icontains=query)
                | albums.filter(album_id__icontains=query)
                | albums.filter(release_date__icontains=query)
                | albums.filter(album_type__icontains=query)
                | albums.filter(artists__name__icontains=query)
            )

    # Apply sorting by ordering, and re-assign the sorted queryset to 'albums'
    albums = albums.order_by(ordering)

    # Paginate the albums
    paginator: Paginator = Paginator(object_list=albums, per_page=10)
    page_number: str | None = request.GET.get("page")
    page_obj: Page = paginator.get_page(number=page_number)

    # Return the rendered template with the context
    return render(
        request=request,
        template_name="spotify_integration/albums.html",
        context={
            "albums": page_obj.object_list,
            "page_obj": page_obj,
            "form": form,
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
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
    sort_by = request.GET.get("sort_by", "name")  # Default to 'name'
    sort_order = request.GET.get("sort_order", "asc")  # Default to ascending order
    valid_sort_fields = ["name", "release_date", "artists__name", "album__name"]
    valid_sort_orders = ["asc", "desc"]

    # Validate the sorting parameters
    if sort_by not in valid_sort_fields:
        sort_by = "name"
    if sort_order not in valid_sort_orders:
        sort_order = "asc"

    # Prepare the ordering string
    ordering = f"{'-' if sort_order == 'desc' else ''}{sort_by}"

    # Initialize the search form and get the songs queryset
    form = SearchForm(data=request.GET)
    songs: QuerySet[Song] = Song.objects.all()

    # Apply search filtering if the form is valid
    if form.is_valid():
        query = form.cleaned_data.get("query")
        if query:
            songs = (
                songs.filter(name__icontains=query)
                | songs.filter(id__icontains=query)
                | songs.filter(release_date__icontains=query)
                | songs.filter(popularity__icontains=query)
                | songs.filter(artists__name__icontains=query)
                | songs.filter(album__name__icontains=query)
            )

    # Apply sorting by ordering
    songs = songs.order_by(ordering)  # Re-assign the result of the ordering

    # Paginate the songs
    paginator: Paginator = Paginator(object_list=songs, per_page=10)
    page_number: str | None = request.GET.get("page")
    page_obj: Page = paginator.get_page(number=page_number)

    # Return the rendered template with the context
    return render(
        request=request,
        template_name="spotify_integration/songs.html",
        context={
            "songs": page_obj.object_list,
            "page_obj": page_obj,
            "form": form,
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
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
            spotify_service.search_all_songs_by_artist(
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
