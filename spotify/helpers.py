import collections

from typing import Dict, Iterable, List

import spotipy

from boltons import iterutils

import objects
import schemas


def get_tracks(spotify: spotipy.Spotify, albums: List[dict]) -> Dict[str, List[objects.SimpleTrack]]:
    tracks = collections.defaultdict(list)

    for album in albums:
        page = album['tracks']

        while page:
            album_tracks = schemas.SimpleTrack(many=True).load(page['items'])
            tracks[album['id']].extend(album_tracks)
            page = spotify.next(page)

    return tracks


def get_albums(spotify: spotipy.Spotify, album_ids: Iterable[str]) -> Dict[str, objects.Album]:
    albums = []

    for album_ids in iterutils.chunked(album_ids, 20):
        albums.extend(spotify.albums(album_ids)['albums'])

    tracks = get_tracks(spotify, albums)

    albums_by_id = {}
    for album in albums:
        album = schemas.Album().load(album)
        album.tracks = tracks[album.id]
        albums_by_id[album.id] = album

    return albums_by_id


def current_user_saved_tracks_contains(spotify: spotipy.Spotify, track_ids: Iterable[str]) -> List[bool]:
    saved = []
    for track_ids in iterutils.chunked(track_ids, 50):
        saved.extend(spotify.current_user_saved_tracks_contains(track_ids))

    return saved
