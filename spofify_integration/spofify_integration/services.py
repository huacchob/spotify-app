import logging
from typing import Any, Union

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

    def object_handling(
        self,
        object_type: Union[Song, Artist, Album],
        obj_params: dict[Any, Any],
    ) -> Union[Song, Artist, Album]:
        """
        Get an object from the database.

        Args:
            object_type (Any): The object to get, Song, Artist, Album.


        Returns:
            Union[Song, Artist, Album]: The object.
        """
        o: Union[Song, Artist, Album] = object_type.objects.filter(**obj_params)
        if o.exists():
            return o.first()
        else:
            raise object_type.DoesNotExist(
                f"Model {object_type} with name {obj_params.get('name')} does not exist",
            )

    def get_or_create_genres(self, name: str) -> Genre:
        """
        Get or create an artist in the database.

        Args:
            name (str): Genre name.

        Returns:
            Genre: Genre object.
        """
        try:
            return Genre.objects.get_or_create(
                name=name,
            )[0]
        except IntegrityError:
            return self.object_handling(
                object_type=Genre,
                obj_params={"name__iexact": name},
            )

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
                artist.genres.add(*list(genres))
                artist.save()
            return artist
        except IntegrityError:
            return self.object_handling(
                object_type=Artist,
                obj_params={"name__iexact": name},
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
                album.artists.add(*list(artists))
                album.save()
            return album
        except IntegrityError:
            return self.object_handling(
                object_type=Album,
                obj_params={"name__iexact": name, "artists": artists},
            )
        except MultipleObjectsReturned:
            return self.object_handling(
                object_type=Album,
                obj_params={"name__iexact": name, "artists": artists},
            )

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
        if len(release_date) != 10:
            release_date = release_date + "-01-01"
        try:
            song, created = Song.objects.get_or_create(
                name=name,
                album=album,
                release_date=release_date,
                popularity=popularity,
            )
            if created:
                song.artists.add(*list(artists))
                song.save()
            return song
        except IntegrityError:
            return self.object_handling(
                object_type=Song,
                obj_params={"name__iexact": name, "album": album},
            )
        except MultipleObjectsReturned:
            return self.object_handling(
                object_type=Song,
                obj_params={"name__iexact": name, "album": album},
            )

    def search_artist(self, artist: str) -> None:
        """
        Get Artist information.

        Args:
            artist (str): Artist name.
        """
        if Artist.objects.filter(name=artist).exists():
            return
        try:
            results: Any | None = self.client.search(
                q=artist,
                type="artist",
                limit=10,
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

        for a in results["artists"]["items"]:
            if artist.lower() != a["name"].lower():
                continue
            genres: set[Genre] = set()
            for genre in a["genres"]:
                if genre and genre != "-":
                    g: Genre = self.get_or_create_genres(
                        name=genre,
                    )
                    genres.add(g)

            self.get_or_create_artist(
                name=a["name"],
                artist_id=a["id"],
                genres=genres,
            )
            return

    def search_artist_and_album(self, artist: str, album_name: str) -> None:
        """
        Get a track from Spotify and create it in the database.

        Args:
            artist (str): Artist name.
            album_name (str): Album name.
        """
        if Album.objects.filter(name=album_name).exists():
            return
        try:
            results: Any | None = self.client.search(
                q=f"{artist} {album_name}",
                type="album",
                limit=10,
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

        for album in results["albums"]["items"]:
            if album_name.lower() != album["name"].lower():
                continue
            album_artists = set()
            for album_artist in album["artists"]:
                if album_artist and album_artist != "-":
                    self.search_artist(artist=album_artist["name"])
                    album_artists.add(
                        self.object_handling(
                            object_type=Artist,
                            obj_params={"name__iexact": album_artist["name"]},
                        )
                    )
            self.get_or_create_album(
                name=album["name"],
                release_date=album["release_date"],
                album_type=album["album_type"],
                artists=album_artists,
                album_id=album["id"],
            )
            return

    def search_artist_and_song(self, artist: str, track_name: str) -> None:
        """
        Get a track from Spotify and create it in the database.

        Args:
            artist (str): Artist name.
            track_name (str): Track name.
        """
        if Song.objects.filter(name=track_name).exists():
            return
        try:
            results: Any | None = self.client.search(
                q=f"{artist} {track_name}",
                type="track",
                limit=10,
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

        for track in results["tracks"]["items"]:
            if track_name.lower() != track["name"].lower():
                continue
            track_artists = set()
            album_artist = ""
            for a_artist in track["album"]["artists"]:
                if a_artist and a_artist != "-":
                    self.search_artist(artist=a_artist["name"])
                    album_artist = a_artist["name"]
            for track_artist in track["artists"]:
                if track_artist and track_artist != "-":
                    self.search_artist(artist=track_artist["name"])
                    track_artists.add(
                        self.object_handling(
                            object_type=Artist,
                            obj_params={"name__iexact": track_artist["name"]},
                        ),
                    )
            self.search_artist_and_album(
                artist=album_artist,
                album_name=track["album"]["name"],
            )
            album: Album = self.object_handling(
                object_type=Album,
                obj_params={"name__iexact": track["album"]["name"]},
            )
            self.get_or_create_song(
                name=track["name"],
                album=album,
                release_date=track["album"]["release_date"],
                popularity=track["popularity"],
                artists=track_artists,
            )
            return

    def search_all_albums_by_artist(self, artist: str) -> None:
        """
        Get Artist information.

        Args:
            artist (str): Artist name.
        """
        self.search_artist(artist=artist)
        main_artist: Artist = self.object_handling(
            object_type=Artist,
            obj_params={"name__iexact": artist},
        )
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
            album_artists: set[Artist] = set()
            for a in album["artists"]:
                if a and a != "-":
                    self.search_artist(artist=a["name"])
                    album_artists.add(
                        self.object_handling(
                            object_type=Artist,
                            obj_params={"name__iexact": a["name"]},
                        )
                    )
                    self.search_artist_and_album(
                        artist=a["name"],
                        album_name=album["name"],
                    )

    def search_all_songs_by_artist(self, artist: str) -> None:
        """
        Get all tracks from an Artist.

        Args:
            artist (str): Artist name.
        """
        self.search_all_albums_by_artist(artist=artist)
        a: Artist = self.object_handling(
            object_type=Artist,
            obj_params={"name__iexact": artist},
        )
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
                song_artists: set[Artist] = set()
                for artist_entry in song["artists"]:
                    if artist_entry and artist_entry != "-":
                        self.search_artist(artist=artist_entry["name"])
                        song_artists.add(
                            self.object_handling(
                                object_type=Artist,
                                obj_params={"name__iexact": artist_entry["name"]},
                            )
                        )
                self.search_artist_and_song(
                    artist=artist,
                    track_name=song["name"],
                )
