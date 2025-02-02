"""
URL configuration for spofify_integration project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import typing as t

from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns: list[t.Any] = [
    path("__debug__/", include("debug_toolbar.urls")),
    path(route="admin/", view=admin.site.urls),
    path(route="", view=views.home, name="home"),  # Root page
    # Artist URLs
    path(route="artists/", view=views.artist_list, name="artist_list"),
    path(
        route="artist/<uuid:artist_id>/",
        view=views.artist_detail,
        name="artist_detail",
    ),
    # Album URLs
    path(
        route="albums/",
        view=views.album_list,
        name="album_list",
    ),
    path(
        route="album/<uuid:album_id>/",
        view=views.album_detail,
        name="album_detail",
    ),
    # Song URLs
    path(
        route="songs/",
        view=views.song_list,
        name="song_list",
    ),
    path(
        route="song/<uuid:song_id>/",
        view=views.song_detail,
        name="song_detail",
    ),
    # Fetch URLs
    path(
        route="fetch-track/",
        view=views.fetch_track_artist_view,
        name="fetch_track",
    ),
    path(
        route="fetch-artist/",
        view=views.fetch_artist_view,
        name="fetch_artist",
    ),
    path(
        route="fetch-artists-albums/",
        view=views.fetch_artist_albums_view,
        name="fetch_artist_albums",
    ),
    path(
        route="fetch-all-songs-from-an-artist/",
        view=views.fetch_all_songs_from_an_artist,
        name="fetch_all_songs_from_an_artist",
    ),
]
