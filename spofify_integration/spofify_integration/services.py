from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import spotipy
from django.conf import settings
from spotipy.oauth2 import SpotifyOAuth

from .models import Album, Artist, Genre, Song

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

    def get_or_create_genres(
        self,
        genres: list[str]
    ) -> list[Genre]:
        """
        Get or create an artist in the database.

        Args:
            genres (list[str]): List of Genre names.

        Returns:
            list[Genre]: List of Genre objects.
        """
        processed_genres: list[Genre] = []
        for genre in genres:
            g: Genre = Genre.objects.get_or_create(name=genre)[0]
            processed_genres.append(g)
        return processed_genres

    def get_or_create_artist(
        self,
        name: str,
        artist_id: str = "",
        genres: list[Genre] = [],
    ) -> Artist:
        """
        Get or create an artist in the database.

        Args:
            name (str): Artist name.
            artist_id (str): Artist Spotify ID.
            genres (list[str]): List of Genre objects.

        Returns:
            Artist: The artist object.
        """
        logger.info(f"Creating artist: {name}")
        artist: Artist = Artist.objects.get_or_create(
            name=name,
        )[0]
        artist.artist_id = artist_id
        artist.genres.add(*genres)
        artist.save()
        return artist

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
        if len(release_date) != 10:
            release_date = release_date + "-01-01"
        album: Album = Album.objects.get_or_create(
            name=name,
            release_date=release_date,
            type=type,
        )[0]
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
        song: Song = Song.objects.get_or_create(
            name=name,
            album=album,
            release_date=release_date,
            popularity=popularity,
        )[0]
        song.artists.add(*artists)
        song.save()
        logger.info(f"Created song: {song}")
        return song

    def search_artist(self, artist: str) -> None:
        """
        Get Artist information.

        Args:
            artist (str): Artist name.
        """
        try:
            results: Any | None = self.client.search(
                q=artist,
                type="artist",
                limit=2,
            )
        except spotipy.SpotifyException as e:
            logger.error(f"Spotify API error: {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error during Spotify search: {e}")
            return

        if not results or not results["artists"]["items"]:
            logger.info(f"No results found for artist: {artist}")
            return

        artist = results["artists"]["items"][0]
        genres: list[Genre] = self.get_or_create_genres(
            genres=artist["genres"],
        )

        self.get_or_create_artist(
            name=artist["name"],
            artist_id=artist["id"],
            genres=genres,
        )

    def search_artist_and_song(self, artist: str, track_name: str) -> None:
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

    def search_all_albums_by_artist(self, artist: str) -> None:
        """
        Get Artist information.

        Args:
            artist (str): Artist name.
        """
        main_artist: Artist = Artist.objects.get_or_create(name=artist)[0]
        if not main_artist.artist_id:
            self.search_artist(artist=main_artist.name)
            main_artist = Artist.objects.get(name=main_artist.name)
        try:
            results: Any | None = self.client.artist_albums(
                artist_id=main_artist.artist_id,
                limit=20,
            )
        except spotipy.SpotifyException as e:
            logger.error(f"Spotify API error: {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error during Spotify search: {e}")
            return

        if not results or not results["items"]:
            logger.info(f"No results found for artist: {artist}")
            return

        albums = results["items"]
        for album in albums:
            album_artists: list[Artist] = []
            for a in album["artists"]:
                album_artist = self.get_or_create_artist(
                    name=a["name"],
                )
                if not album_artist.artist_id:
                    self.search_artist(artist=album_artist.name)
                    album_artist: Artist = Artist.objects.get(
                        name=album_artist.name,
                    )
                album_artists.append(
                    album_artist,
                )
            self.get_or_create_album(
                name=album["name"],
                release_date=album["release_date"],
                type=album["album_type"],
                artists=album_artists,
            )
