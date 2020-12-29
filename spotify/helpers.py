import collections

from typing import Dict, Iterable, List

from boltons import iterutils

import client
import objects
import schemas


def get_tracks(albums: List[dict]) -> Dict[str, List[objects.SimpleTrack]]:
    spotify = client.spotify_client()
    tracks = collections.defaultdict(list)

    for album in albums:
        page = album['tracks']

        while page:
            album_tracks = schemas.SimpleTrack(many=True).load(page['items'])
            tracks[album['id']].extend(album_tracks)
            page = spotify.next(page)

    return tracks


def get_albums(album_ids: Iterable[str]) -> Dict[str, objects.Album]:
    spotify = client.spotify_client()
    albums = []

    for album_ids in iterutils.chunked(album_ids, 20):
        albums.extend(spotify.albums(album_ids)['albums'])

    tracks = get_tracks(albums)

    albums_by_id = {}
    for album in albums:
        album = schemas.Album().load(album)
        album.tracks = tracks[album.id]
        albums_by_id[album.id] = album

    return albums_by_id


def current_user_saved_tracks_contains(track_ids: Iterable[str]) -> List[bool]:
    spotify = client.spotify_client()
    saved = []

    for track_ids in iterutils.chunked(track_ids, 50):
        saved.extend(spotify.current_user_saved_tracks_contains(track_ids))

    return saved
