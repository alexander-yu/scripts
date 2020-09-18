import collections

import click
import spotipy

import client

PAGE_LIMIT = 50


def get_unsaved_albums(spotify: spotipy.Spotify, tracks: list) -> list:
    albums_by_id = collections.OrderedDict()

    for track in tracks:
        album = track['track']['album']
        albums_by_id[album['id']] = album

    saved = spotify.current_user_saved_albums_contains(list(albums_by_id.keys()))

    unsaved_albums = []
    for album_id, saved in zip(albums_by_id.keys(), saved):
        if not saved:
            unsaved_albums.append(albums_by_id[album_id])

    return unsaved_albums


def get_artists(album: dict):
    return [artist['name'] for artist in album['artists']]


def save_albums(spotify: spotipy.Spotify, page: dict):
    page.pop('items')
    print(page)
    unsaved_albums = get_unsaved_albums(spotify, page['items'])

    lines = []
    for i, album in enumerate(unsaved_albums):
        lines.append('{:>2}. {} {}'.format(i + 1, album['name'], '[{artists}]'.format(artists=', '.join(get_artists(album)))))

    if unsaved_albums:
        click.echo_via_pager('\n'.join(lines))

        if click.confirm('Save all?'):
            album_ids = [album['id'] for album in unsaved_albums]
            spotify.current_user_saved_albums_add(album_ids)
        else:
            while True:
                indices = click.prompt('Indicate the indices of the albums you would like to save (ex: 1, 2, 5)')
                try:
                    indices = [int(index.strip()) for index in indices.split(',')]
                except ValueError:
                    click.echo('"{indices}" was not a valid list of indices.'.format(indices=indices))
                finally:
                    break

            album_ids = [unsaved_albums[index - 1]['id'] for index in indices]
            spotify.current_user_saved_albums_add(album_ids)

        click.clear()


@click.command()
def run():
    spotify = client.spotify_client()
    page = spotify.current_user_saved_tracks(limit=PAGE_LIMIT)
    save_albums(spotify, page)

    while page:
        page = spotify.next(page)
        save_albums(spotify, page)


if __name__ == '__main__':
    run()
