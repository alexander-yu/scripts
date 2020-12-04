import collections
import itertools

from typing import Dict, Iterable

import click
import spotipy

import client
import helpers
import objects
import schemas

PAGE_LIMIT = 50
AUTOSAVE_THRESHOLD = 0.6


def get_unsaved_albums(spotify: spotipy.Spotify, albums_by_id: Dict[str, objects.Album]) -> Iterable[objects.Album]:
    saved = spotify.current_user_saved_albums_contains(list(albums_by_id.keys()))

    unsaved_albums = {}
    for album_id, album_is_saved in zip(albums_by_id.keys(), saved):
        if not album_is_saved:
            unsaved_albums[album_id] = albums_by_id[album_id]

    autosaved_albums = autosave_albums(spotify, unsaved_albums)
    for album_id in autosaved_albums:
        unsaved_albums.pop(album_id)

    return unsaved_albums.values()


def autosave_albums(spotify: spotipy.Spotify, unsaved_albums: Dict[str, objects.Album]):
    albums_by_track = {
        track.id: album
        for album in unsaved_albums.values()
        for track in album.tracks
    }
    track_ids = [
        track.id
        for track in itertools.chain.from_iterable([
            album.tracks
            for album in unsaved_albums.values()
        ])
    ]
    saved = helpers.current_user_saved_tracks_contains(spotify, track_ids)

    album_save_counts = collections.defaultdict(int)
    for track_id, track_is_saved in zip(track_ids, saved):
        album = albums_by_track[track_id]
        if track_is_saved:
            album_save_counts[album.id] += 1

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


def get_albums_by_id(spotify: spotipy.Spotify, page: dict) -> Dict[str, objects.Album]:
    page = schemas.Page().load(page)
    album_ids = []

    for track in page.items:
        track = schemas.SavedTrack().load(track)
        album_ids.append(track.track.album.id)

    return helpers.get_albums(spotify, album_ids)


def save_albums(spotify: spotipy.Spotify, page: dict):
    albums_by_id = get_albums_by_id(spotify, page)
    unsaved_albums = get_unsaved_albums(spotify, albums_by_id)

    lines = []
    for i, album in enumerate(unsaved_albums):
        lines.append('{:>2}. {}'.format(i + 1, album))

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
                    indices = [int(index.strip()) for index in indices.split(',')]
                except ValueError:
                    click.echo('"{indices}" was not a valid list of indices.'.format(indices=indices))
                finally:
                    break  # pylint: disable=lost-exception

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
        save_albums(spotify, page)
        bar.update(len(page['items']))

        while page:
            page = spotify.next(page)
            save_albums(spotify, page)
            bar.update(len(page['items']))


if __name__ == '__main__':
    run()
