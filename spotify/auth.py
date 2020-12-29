import click
import keyring


CLIENT_ID_KEY = 'Spotify Client ID'
SYSTEM = 'ayu:scripts:spotify'


def get_client_id() -> str:
    client_id = keyring.get_password(SYSTEM, CLIENT_ID_KEY)

    if client_id:
        return client_id

    client_id = click.prompt('Please enter your Spotify client ID')
    keyring.set_password(SYSTEM, CLIENT_ID_KEY, client_id)
    return client_id


def get_client_secret(client_id: str) -> str:
    secret = keyring.get_password(SYSTEM, client_id)

    if secret:
        return secret

    secret = click.prompt('Please enter your Spotify client secret', hide_input=True, confirmation_prompt=True)
    keyring.set_password(SYSTEM, client_id, secret)
    return secret
