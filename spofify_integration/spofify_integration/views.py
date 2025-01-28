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
    Home view.

    Args:
        request (HttpRequest): Request object passed from urls module.

    Returns:
        HttpResponse: Response object with home page template.
    """
    artists: QuerySet[Artist] = Artist.objects.all()
    return render(
        request=request,
        template_name="spotify_integration/artists.html",
        context={"artists": artists},
    )


def artist_detail(request: HttpRequest, artist_id: int) -> HttpResponse:
    """
    Home view.

    Args:
        request (HttpRequest): Request object passed from urls module.
        artist_id (int): Artist id passed from urls module.

    Returns:
        HttpResponse: Response object with home page template.
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
