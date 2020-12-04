import pprint

import click

import client


@click.command()
@click.argument('album_id')
@click.option('--include_tracks', default=False, help='Whether or not to include tracks in the output')
@click.option('--include_markets', default=False, help='Whether or not to include markets in the output')
def run(album_id, include_tracks, include_markets):
    spotify = client.spotify_client()
    album = spotify.album(album_id)

    if not include_tracks:
        album.pop('tracks')
    if not include_markets:
        album.pop('available_markets')

    pprint.pprint(album)


if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
