import cachetools
import spotipy
import spotipy.oauth2

import auth


CACHE_PATH = '.cache'
REDIRECT_URI = 'https://localhost:5000/callback'
SCOPES = ' '.join([
    'user-library-modify',
    'user-library-read',
])


@cachetools.cached(cachetools.Cache(1))
def spotify_client() -> spotipy.Spotify:
    client_id = auth.get_client_id()
    client_secret = auth.get_client_secret(client_id)

    auth_manager = spotipy.oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=CACHE_PATH,
        open_browser=False,
    )

    return spotipy.Spotify(auth_manager=auth_manager)
