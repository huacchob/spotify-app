from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import spotipy
from django.conf import settings
from spotipy.oauth2 import SpotifyOAuth

from .models import Album, Artist, Song

if TYPE_CHECKING:
    from spotipy.client import Spotify


logger = logging.getLogger(__name__)


class SpotifyService:
    def __init__(self):
        """
        Initialize the Spotify client using credentials from Django settings.
        """
        self.client: Spotify = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
                redirect_uri="http://example.com",
                scope="user-library-read",
            ),
        )

    def search_query(self, artist: str, track_name: str) -> None:
        """
        Get a track from Spotify and create it in the database.

        Args:
            artist (str): Artist name.
            track_name (str): Track name.
        """
        try:
            results: Any | None = self.client.search(
                q=f"artist:{artist} track:{track_name}",
                type="track",
                limit=2,
            )
        except spotipy.SpotifyException as e:
            logger.error(f"Spotify API error: {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error during Spotify search: {e}")
            return

        if not results or not results["tracks"]["items"]:
            logger.info(f"No results found for artist: {artist}, track: {track_name}")
            return

        track = results["tracks"]["items"][0]

        track_artists = []
        album_artists = []
        for album_artist in track["album"]["artists"]:
            a_a = self.get_or_create_artist(
                name=album_artist["name"],
            )
            album_artists.append(
                a_a,
            )
        for track_artist in track["artists"]:
            t_a = self.get_or_create_artist(
                name=track_artist["name"],
            )
            track_artists.append(
                t_a,
            )
        album = self.get_or_create_album(
            name=track["album"]["name"],
            release_date=track["album"]["release_date"],
            type=track["album"]["album_type"],
            artists=album_artists,
        )
        self.get_or_create_song(
            name=track["name"],
            album=album,
            release_date=track["album"]["release_date"],
            popularity=track["popularity"],
            artists=track_artists,
        )

    def get_or_create_artist(self, name: str) -> Artist:
        """
        Get or create an artist in the database.

        Args:
            name (str): Artist name.

        Returns:
            Artist: The artist object.
        """
        logger.info(f"Creating artist: {name}")
        return Artist.objects.get_or_create(name=name)[0]

    def get_or_create_album(
        self,
        name: str,
        release_date: str,
        type: str,
        artists: list[Artist],
    ) -> Album:
        """
        Get or create an album in the database.

        Args:
            name (str): Album name.
            release_date (str): Release date.
            type (str): Album type.
            artists (list[Artist]): List of artists.

        Returns:
            Album: The album object.
        """
        album, created = Album.objects.get_or_create(
            name=name,
            release_date=release_date,
            type=type,
        )
        if created:
            album.artists.set(artists)
            album.save()
        else:
            album.artists.add(*artists)
            album.save()
        logger.info(f"Created album: {album}")
        return album

    def get_or_create_song(
        self,
        name: str,
        album: Album,
        release_date: str,
        popularity: int,
        artists: list[Artist],
    ) -> Song:
        """
        Get or create a song in the database.

        Args:
            name (str): Song name.
            album (Album): Album object.
            release_date (str): Release date.
            popularity (int): Popularity score.
            artists (list[Artist]): List of artists.

        Returns:
            Song: The song object.
        """
        song, created = Song.objects.get_or_create(
            name=name,
            album=album,
            release_date=release_date,
            popularity=popularity,
        )
        for artist in artists:
            song.artists.add(artist)
            song.save()
        logger.info(f"Created song: {song}")
        return song
