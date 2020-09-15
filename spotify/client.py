import configparser

import cachetools
import spotipy
import spotipy.oauth2


CACHE_PATH = '.cache'
REDIRECT_URI = 'https://localhost:5000/callback'
SCOPES = ' '.join([
    'user-library-modify',
    'user-library-read',
])


@cachetools.cached(cachetools.Cache(1))
def spotify_client() -> spotipy.Spotify:
    config = configparser.ConfigParser()
    config.read('secrets.ini')
    client_id = config['client']['id']
    client_secret = config['client']['secret']

    auth_manager = spotipy.oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=CACHE_PATH,
        # TODO (ayu): use open_browser=False and go browserless when spotipy is next updated
    )

    return spotipy.Spotify(auth_manager=auth_manager)
