import logging
from typing import Any

import spotipy
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from django.db.models import QuerySet
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyOAuth

from .models import Album, Artist, Genre, Song

logger: logging.Logger = logging.getLogger(name=__name__)


class SpotifyService:
    def __init__(self) -> None:
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
        artist_id: str,
        genres: list[Genre],
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
        try:
            artist, created = Artist.objects.get_or_create(
                name=name,
                artist_id=artist_id,
            )
            if created:
                artist.genres.add(*genres)
                artist.save()
            return artist
        except IntegrityError:
            return Artist.objects.get(
                name=name,
            )

    def get_or_create_album(
        self,
        name: str,
        release_date: str,
        album_type: str,
        artists: list[Artist],
        album_id: str = "",
    ) -> Album:
        """
        Get or create an album in the database.

        Args:
            name (str): Album name.
            release_date (str): Release date.
            album_type (str): Album type.
            artists (list[Artist]): List of artists.
            album_id (str): Spotify Album ID.

        Returns:
            Album: The album object.
        """
        if len(release_date) != 10:
            release_date = release_date + "-01-01"
        try:
            album, created = Album.objects.get_or_create(
                name=name,
                release_date=release_date,
                album_type=album_type,
                album_id=album_id,
            )
            if created:
                album.artists.add(*artists)
                album.save()
            return album
        except IntegrityError:
            return Album.objects.get(
                name=name,
                release_date=release_date,
            )
        except MultipleObjectsReturned:
            return Album.objects.filter(
                name=name,
                artists=artists,
            ).first()

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
        try:
            song, created = Song.objects.get_or_create(
                name=name,
                album=album,
                release_date=release_date,
                popularity=popularity,
            )
            if created:
                song.artists.add(*artists)
                song.save()
            return song
        except IntegrityError:
            return Song.objects.get(
                name=name,
                album=album,
            )
        except MultipleObjectsReturned:
            return Song.objects.filter(
                name=name,
                album=album,
            ).first()

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

    def search_artist_and_album(self, artist: str, album_name: str) -> None:
        """
        Get a track from Spotify and create it in the database.

        Args:
            artist (str): Artist name.
            album_name (str): Album name.
        """
        try:
            results: Any | None = self.client.search(
                q=f"{artist} {album_name}",
                type="album",
                limit=2,
            )
        except spotipy.SpotifyException as e:
            logger.error(f"Spotify API error: {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error during Spotify search: {e}")
            return

        if not results or not results["albums"]["items"]:
            logger.info(f"No results found for artist: {artist}, track: {album_name}")
            return

        album = results["albums"]["items"][0]

        album_artists = []
        for album_artist in album["artists"]:
            self.search_artist(artist=album_artist["name"])
            album_artists.append(
                Artist.objects.get(name=album_artist["name"]),
            )
        self.get_or_create_album(
            name=album["name"],
            release_date=album["release_date"],
            album_type=album["album_type"],
            artists=album_artists,
            album_id=album["id"],
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
                q=f"{artist} {track_name}",
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
            self.search_artist(artist=album_artist["name"])
            album_artists.append(
                Artist.objects.get(name=album_artist["name"]),
            )
        for track_artist in track["artists"]:
            self.search_artist(artist=track_artist["name"])
            track_artists.append(
                Artist.objects.get(name=track_artist["name"]),
            )
        self.search_artist_and_album(
            artist=artist,
            album_name=track["album"]["name"],
        )
        album: Album = Album.objects.get(name=track["album"]["name"])
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
        self.search_artist(artist=artist)
        main_artist: Artist = Artist.objects.get(name=artist)
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
                self.search_artist(artist=a["name"])
                album_artists.append(Artist.objects.get(name=a["name"]))
                self.search_artist_and_album(
                    artist=a["name"],
                    album_name=album["name"],
                )
            self.search_artist_and_album(
                artist=artist,
                album_name=album["name"],
            )

    def search_all_songs_by_artist(self, artist: str) -> None:
        """
        Get all tracks from an Artist.

        Args:
            artist (str): Artist name.
        """
        self.search_all_albums_by_artist(artist=artist)
        a: Artist = Artist.objects.get(name__iexact=artist)
        all_albums: QuerySet[Album] = a.albums.all()
        for album in all_albums:
            try:
                results: Any | None = self.client.album_tracks(
                    album_id=album.album_id,
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
            
            album_songs = results["items"]
            for song in album_songs:
                song_artists: list[Artist] = []
                for artist_entry in song["artists"]:
                    self.search_artist(artist=artist_entry["name"])
                    song_artists.append(
                        Artist.objects.get(name=artist_entry["name"]),
                    )
                self.search_artist_and_song(
                    artist=artist,
                    track_name=song["name"],
                )
