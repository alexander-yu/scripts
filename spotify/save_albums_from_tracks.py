import collections
import itertools
import json
import os

from typing import Dict, Iterable, List, Tuple

import click

import client
import helpers
import objects
import schemas

CACHE_PATH = '.save_albums_cache'
PAGE_LIMIT = 50
AUTOSAVE_THRESHOLD = 0.6


def get_unsaved_albums(albums_by_id: Dict[str, objects.Album]) -> Tuple[Iterable[objects.Album], Dict[str, int]]:
    spotify = client.spotify_client()
    album_ids = list(albums_by_id.keys())
    saved = spotify.current_user_saved_albums_contains(album_ids)

    unsaved_albums = {}
    for album_id, album_is_saved in zip(album_ids, saved):
        if not album_is_saved:
            unsaved_albums[album_id] = albums_by_id[album_id]

    album_save_counts = get_album_save_counts(list(unsaved_albums.values()))
    autosaved_albums = autosave_albums(unsaved_albums, album_save_counts)

    for album_id in autosaved_albums:
        unsaved_albums.pop(album_id)

    return unsaved_albums.values(), album_save_counts


def get_album_save_counts(albums: List[objects.Album]) -> Dict[str, int]:
    albums_by_track = {
        track.id: album
        for album in albums
        for track in album.tracks
    }
    track_ids = [
        track.id
        for track in itertools.chain.from_iterable([
            album.tracks
            for album in albums
        ])
    ]
    saved = helpers.current_user_saved_tracks_contains(track_ids)

    album_save_counts = collections.defaultdict(int)
    for track_id, track_is_saved in zip(track_ids, saved):
        album = albums_by_track[track_id]
        if track_is_saved:
            album_save_counts[album.id] += 1

    return album_save_counts


def autosave_albums(unsaved_albums: Dict[str, objects.Album], album_save_counts: Dict[str, int]) -> List[str]:
    spotify = client.spotify_client()
    albums_to_save = [
        album_id
        for album_id in album_save_counts
        if album_save_counts[album_id] / len(unsaved_albums[album_id].tracks) >= AUTOSAVE_THRESHOLD
    ]

    if albums_to_save:
        click.echo_via_pager(
            '\n'.join(
                ['Autosaving the following albums:'] + [str(unsaved_albums[album_id]) for album_id in albums_to_save]
            ) + '\n'
        )
        spotify.current_user_saved_albums_add(albums_to_save)

    return albums_to_save


def get_albums_by_id(page: dict) -> Dict[str, objects.Album]:
    page = schemas.Page().load(page)
    album_ids = []

    for track in page.items:
        track = schemas.SavedTrack().load(track)
        album_ids.append(track.track.album.id)

    return helpers.get_albums(album_ids)


def get_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r') as file:
            return json.load(file)

    return {'skipped': []}


def save_albums(page: dict):
    spotify = client.spotify_client()
    albums_by_id = get_albums_by_id(page)
    unsaved_albums, album_save_counts = get_unsaved_albums(albums_by_id)

    cache = get_cache()
    skipped = set(cache['skipped'])

    unsaved_albums = [album for album in unsaved_albums if album.id not in skipped]

    lines = []
    for i, album in enumerate(unsaved_albums):
        lines.append(f'{i + 1:>2}. {album} ({album_save_counts[album.id]}/{len(album.tracks)})')

    if unsaved_albums:
        click.echo_via_pager('\n'.join(lines))

        if click.confirm('Save all?'):
            album_ids = [album.id for album in unsaved_albums]
            spotify.current_user_saved_albums_add(album_ids)
        else:
            while True:
                indices = click.prompt(
                    'Indicate the indices of the albums you would like to save (ex: 1, 2, 5); '
                    'enter nothing if you want to skip',
                    default='',
                    show_default=False,
                )
                try:
                    if indices:
                        indices = set(int(index.strip()) for index in indices.split(','))
                    else:
                        indices = set()
                except ValueError:
                    click.echo('"{indices}" was not a valid list of indices.'.format(indices=indices))
                finally:
                    break  # pylint: disable=lost-exception

            skipped.update(album.id for index, album in enumerate(unsaved_albums) if index + 1 not in indices)
            cache['skipped'] = list(skipped)

            with open(CACHE_PATH, 'w') as file:
                json.dump(cache, file)

            if indices:
                album_ids = [unsaved_albums[index - 1].id for index in indices]
                spotify.current_user_saved_albums_add(album_ids)

        click.clear()


@click.command()
def run():
    spotify = client.spotify_client()
    page = spotify.current_user_saved_tracks(limit=PAGE_LIMIT)
    total = page['total']

    with click.progressbar(length=total) as bar:
        while page:
            save_albums(page)
            bar.update(len(page['items']))
            page = spotify.next(page)


if __name__ == '__main__':
    run()
